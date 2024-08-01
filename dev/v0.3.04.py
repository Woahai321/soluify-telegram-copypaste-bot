import asyncio
import random
import re
import sys
import time
import json
import signal
import logging
import os
import select
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError, RPCError, ChatForwardsRestrictedError
from colorama import init, Fore, Style
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass

init(autoreset=True)

# Define color schemes
MAIN_COLOR_START = (147, 112, 219)  # Medium Purple
MAIN_COLOR_END = (0, 191, 255)      # Deep Sky Blue
ALERT_COLOR = (255, 69, 0)          # Red-Orange
SUCCESS_COLOR = (50, 205, 50)       # Lime Green
PROMPT_COLOR_START = (0, 255, 255)  # Cyan
PROMPT_COLOR_END = (135, 206, 250)  # Light Sky Blue

CONFIG_FILE = 'telegramconfiguration.json'
CREDENTIALS_FILE = 'credentials.json'
LOG_FILE = 'soluify.log'

MAX_RETRIES = 3
RETRY_DELAY = 5

def setup_logger():
    logger = logging.getLogger('soluify')
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.ERROR)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

def gradient_text(text, start_color, end_color, emoji=None):
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    gradient = []
    length = len(text)
    for i, char in enumerate(text):
        r = start_r + (end_r - start_r) * i / length
        g = start_g + (end_g - start_g) * i / length
        b = start_b + (end_b - start_b) * i / length
        gradient.append(f"\033[38;2;{int(r)};{int(g)};{int(b)}m{char}\033[0m")
    result = ''.join(gradient)
    if emoji:
        result += f" {emoji}"
    return result

async def animated_transition(text, duration=0.5):
    emojis = ["✨", "🚀", "💫", "🌟", "💡", "🔮", "🎉"]
    for _ in range(int(duration * 10)):
        emoji = random.choice(emojis)
        print(f"\r{gradient_text(text, MAIN_COLOR_START, MAIN_COLOR_END, emoji)}", end="", flush=True)
        await asyncio.sleep(0.05)
    print()

def get_key(password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'soluify_salt',  # In production, use a random salt and store it
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data, password):
    key = get_key(password)
    f = Fernet(key)
    return f.encrypt(json.dumps(data).encode())

def decrypt_data(encrypted_data, password):
    key = get_key(password)
    f = Fernet(key)
    return json.loads(f.decrypt(encrypted_data).decode())

def store_credentials():
    # Display the security warning first
    print(gradient_text("SECURITY WARNING", ALERT_COLOR, ALERT_COLOR, "🚨"))
    print(gradient_text("You are about to interact with your API credentials for your Telegram account.", ALERT_COLOR, ALERT_COLOR))
    print(gradient_text("These should be treated with the same level of security as your bank details.", ALERT_COLOR, ALERT_COLOR))
    print(gradient_text("Please ensure you're in a secure environment before proceeding.", ALERT_COLOR, ALERT_COLOR))

    proceed = input(gradient_text("Do you wish to proceed? (y/n): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    if proceed.lower() != 'y':
        print(gradient_text("Operation cancelled. Exiting for your security.", MAIN_COLOR_START, MAIN_COLOR_END))
        exit()

    # Now prompt for the API details
    api_id = getpass.getpass(gradient_text("Please enter your API ID: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    api_hash = getpass.getpass(gradient_text("Please enter your API Hash: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    phone_number = input(gradient_text("Please enter your phone number (e.g., 447123456789): ", PROMPT_COLOR_START, PROMPT_COLOR_END))

    save_choice = input(gradient_text("Do you wish to save your login credentials for future use (stay signed in)? (y/n): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    print(gradient_text("From a security perspective, saving credentials is not recommended.", ALERT_COLOR, ALERT_COLOR, "⚠️"))

    if save_choice.lower() == 'y':
        password = getpass.getpass(gradient_text("Enter a strong password to encrypt your credentials: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        credentials = {
            'api_id': api_id,
            'api_hash': api_hash,
            'phone_number': phone_number
        }
        encrypted_data = encrypt_data(credentials, password)
        with open(CREDENTIALS_FILE, 'wb') as f:
            f.write(encrypted_data)
        print(gradient_text("Credentials saved and encrypted.", SUCCESS_COLOR, SUCCESS_COLOR, "🔐"))
    else:
        print(gradient_text("Credentials will not be saved. They will be deleted when you exit the script.", MAIN_COLOR_START, MAIN_COLOR_END))

    return save_choice.lower() == 'y'

def read_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        password = getpass.getpass(gradient_text("Enter your password to decrypt credentials: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        try:
            with open(CREDENTIALS_FILE, 'rb') as f:
                encrypted_data = f.read()
            credentials = decrypt_data(encrypted_data, password)
            print(gradient_text("Credentials successfully decrypted! Welcome back!", SUCCESS_COLOR, SUCCESS_COLOR, "🎉"))
            return credentials['api_id'], credentials['api_hash'], credentials['phone_number']
        except Exception as e:
            logger.error(f"Error reading credentials: {e}")
            print(gradient_text(f"Oops! Error reading credentials: {e}. Let's try again!", ALERT_COLOR, ALERT_COLOR))
            return None, None, None
    else:
        print(gradient_text("No saved credentials found. Time for a fresh start!", MAIN_COLOR_START, MAIN_COLOR_END, "🕵️"))
        return None, None, None

class TelegramForwarder:
    def __init__(self, client, phone_number):
        self.client = client
        self.phone_number = phone_number
        self.blacklist = []
        self.running = False

    async def connect_with_retry(self):
        for attempt in range(MAX_RETRIES):
            try:
                await self.client.connect()
                if not await self.client.is_user_authorized():
                    await self.client.send_code_request(self.phone_number)
                    try:
                        await self.client.sign_in(self.phone_number, getpass.getpass(gradient_text('Enter the code: ', PROMPT_COLOR_START, PROMPT_COLOR_END)))
                    except SessionPasswordNeededError:
                        await self.client.sign_in(password=getpass.getpass(gradient_text('Two step verification is enabled. Please enter your password: ', PROMPT_COLOR_START, PROMPT_COLOR_END)))
                print(gradient_text("Successfully connected to Telegram!", SUCCESS_COLOR, SUCCESS_COLOR, "✅"))
                return True
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                print(gradient_text(f"Connection attempt {attempt + 1} failed. Retrying in {RETRY_DELAY} seconds...", ALERT_COLOR, ALERT_COLOR))
                await asyncio.sleep(RETRY_DELAY)
        print(gradient_text(f"Failed to connect after {MAX_RETRIES} attempts. Please check your internet connection and try again.", ALERT_COLOR, ALERT_COLOR))
        return False

    async def list_chats(self):
        if not await self.connect_with_retry():
            return

        dialogs = await self.client.get_dialogs()
        
        with open(f"chats_of_{self.phone_number}.txt", "w") as chats_file, tqdm(total=len(dialogs), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=75, colour="blue") as pbar:
            for dialog in dialogs:
                chat_info = f"Chat ID: {dialog.id}, Title: {dialog.title}"
                print(gradient_text(chat_info, MAIN_COLOR_START, MAIN_COLOR_END))
                chats_file.write(chat_info + "\n")
                pbar.update(1)
        
        print(gradient_text("All your chats are listed! Time to choose your favorites!", SUCCESS_COLOR, SUCCESS_COLOR, "🎉"))

    async def forward_messages_to_channels(self, source_chat_ids, destination_channel_ids, keywords, signature):
        if not await self.connect_with_retry():
            return

        self.running = True
        last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

        while self.running:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(gradient_text(f"[{timestamp}] Soluify is on the lookout for new messages...", MAIN_COLOR_START, MAIN_COLOR_END, "👀"))
            print(gradient_text("Type 'exit' and press Enter to stop forwarding and return to the main menu.", MAIN_COLOR_START, MAIN_COLOR_END))

            # Check for user input to exit
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = input().strip()
                if line.lower() == 'exit':
                    print(gradient_text("Stopping message forwarding...", MAIN_COLOR_START, MAIN_COLOR_END))
                    self.running = False
                    break

            try:
                for chat_id in source_chat_ids:
                    messages = await self.client.get_messages(chat_id, min_id=last_message_ids[chat_id], limit=None)

                    for message in reversed(messages):
                        should_forward = False
                        if keywords:
                            if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
                                should_forward = True
                        else:
                            should_forward = True

                        if should_forward and not any(word.lower() in message.text.lower() for word in self.blacklist):
                            if message.text:
                                for dest_id in destination_channel_ids:
                                    await self.client.send_message(dest_id, message.message + f"\n\n**{signature}**")
                            if message.media:
                                # Download the media
                                media_path = await self.client.download_media(message.media)
                                for dest_id in destination_channel_ids:
                                    # Re-upload the media with a new message
                                    await self.client.send_file(dest_id, media_path, caption=f"{message.text}\n\n**{signature}**" if message.text else f"**{signature}**")
                        
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(gradient_text(f"[{timestamp}] Message forwarded with your signature!", SUCCESS_COLOR, SUCCESS_COLOR, "✅"))

                        last_message_ids[chat_id] = max(last_message_ids[chat_id], message.id)

            except FloodWaitError as e:
                logger.error(f"Flood wait error: {e}. Waiting for {e.seconds} seconds before retrying.")
                print(gradient_text(f"Whoa there! Flood wait error: {e}. Taking a {e.seconds} second breather before we dive back in!", ALERT_COLOR, ALERT_COLOR))
                await asyncio.sleep(e.seconds)
            except RPCError as e:
                logger.error(f"RPC error: {e}")
                print(gradient_text(f"RPC error: {e}. Let's check those internet pipes and try again!", ALERT_COLOR, ALERT_COLOR))
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(gradient_text(f"Unexpected twist in our adventure: {e}", ALERT_COLOR, ALERT_COLOR))

            await asyncio.sleep(5)

def load_profiles():
    try:
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_profile(profile_name, config):
    profiles = load_profiles()
    profiles[profile_name] = config
    with open(CONFIG_FILE, 'w') as file:
        json.dump(profiles, file, indent=4)

def edit_profile(profile_name):
    profiles = load_profiles()
    if profile_name not in profiles:
        print(gradient_text(f"Profile '{profile_name}' not found.", ALERT_COLOR, ALERT_COLOR))
        return

    config = profiles[profile_name]
    print(gradient_text(f"Editing profile: {profile_name}", MAIN_COLOR_START, MAIN_COLOR_END))
    
    config['source_chat_ids'] = input(gradient_text("Enter the source chat IDs (comma separated): ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    config['source_chat_ids'] = [int(chat_id.strip()) for chat_id in config['source_chat_ids']]
    
    config['destination_channel_ids'] = input(gradient_text("Enter the destination chat IDs (comma separated): ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    config['destination_channel_ids'] = [int(chat_id.strip()) for chat_id in config['destination_channel_ids']]
    
    config['keywords'] = input(gradient_text("Enter keywords to filter messages (optional, comma separated): ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    config['keywords'] = [keyword.strip() for keyword in config['keywords'] if keyword.strip()]
    
    config['signature'] = input(gradient_text("Enter the signature to append to each message: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    
    config['blacklist'] = input(gradient_text("Enter blacklisted words (comma separated, or leave blank): ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    config['blacklist'] = [word.strip().lower() for word in config['blacklist'] if word.strip()]

    profiles[profile_name] = config
    save_profile(profile_name, config)
    print(gradient_text(f"Profile '{profile_name}' has been updated.", SUCCESS_COLOR, SUCCESS_COLOR, "✅"))

async def graceful_shutdown(credentials_saved, phone_number):
    if credentials_saved:
        print(gradient_text("Your encrypted credentials will be kept for future use.", MAIN_COLOR_START, MAIN_COLOR_END, "🔒"))
    else:
        print(gradient_text("Preparing to delete temporary credentials and session files...", MAIN_COLOR_START, MAIN_COLOR_END, "🧹"))
    
    action = "SAVE" if credentials_saved else "DELETE"
    print(gradient_text(f"IMPORTANT: You have chosen to {action} your credentials upon exit.", ALERT_COLOR, ALERT_COLOR, "⚠️"))
    confirm = input(gradient_text(f"Are you absolutely sure you want to {action} your credentials? (y/n): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    
    if confirm.lower() == 'y':
        if not credentials_saved:
            try:
                os.remove(CREDENTIALS_FILE)
                os.remove(f'session_{phone_number}.session')
                print(gradient_text("Temporary credentials and session files have been deleted.", SUCCESS_COLOR, SUCCESS_COLOR, "✅"))
            except Exception as e:
                logger.error(f"Error while deleting files: {e}")
                print(gradient_text(f"Error while deleting files: {e}", ALERT_COLOR, ALERT_COLOR))
        print(gradient_text("Soluify is signing off. Your choices have been applied. Stay safe!", SUCCESS_COLOR, SUCCESS_COLOR, "🌙"))
    else:
        print(gradient_text("Operation cancelled. No changes were made to your credentials.", MAIN_COLOR_START, MAIN_COLOR_END))
        if credentials_saved:
            # If the user previously chose to save credentials but now decides not to, delete the credentials file
            try:
                os.remove(CREDENTIALS_FILE)
                print(gradient_text("Credentials file has been deleted as per your request.", SUCCESS_COLOR, SUCCESS_COLOR, "✅"))
            except Exception as e:
                logger.error(f"Error while deleting credentials file: {e}")
                print(gradient_text(f"Error while deleting credentials file: {e}", ALERT_COLOR, ALERT_COLOR))
        print(gradient_text("Please run the script again if you want to make changes.", MAIN_COLOR_START, MAIN_COLOR_END))

    # Add a final confirmation before exiting
    input(gradient_text("Press Enter to exit the script...", PROMPT_COLOR_START, PROMPT_COLOR_END))

async def display_help():
    help_text = """
    🌟 Soluify Telegram Copy & Paste Bot Help 🌟
    ===========================================
    
    1. List Chats: 
       - Displays all your Telegram chats and their IDs.
       - Use these IDs to set up source and destination chats.

    2. Set Up Message Forwarding:
       - Configure the bot to forward messages from source to destination chats.
       - You can set keywords to filter messages and add a signature.

    3. Edit Profile:
       - Modify existing configuration profiles.

    4. Exit:
       - Safely close the application, with options to save or delete credentials.

    💡 Tips:
    - Always keep your API credentials secure.
    - Use keywords to filter messages effectively.
    - Remember to type 'exit' when you want to stop message forwarding.

    If you need more help, feel free to reach out to our support team!
    """
    print(gradient_text(help_text, MAIN_COLOR_START, MAIN_COLOR_END))
    input(gradient_text("Press Enter to return to the main menu...", PROMPT_COLOR_START, PROMPT_COLOR_END))

async def matrix_effect(logo_frames):
    logo_width = max(len(line) for line in logo_frames)
    logo_height = len(logo_frames)
    matrix = [[' ' for _ in range(logo_width)] for _ in range(logo_height)]
    matrix_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,.<>?"
    
    for frame in atqdm(range(50), desc="Loading", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=75, colour="magenta"):
        print("\033[H\033[J", end="")  # Clear screen
        
        # Update matrix
        for col in range(logo_width):
            if random.random() < 0.2:  # Chance to start a new "drop"
                matrix[0][col] = random.choice(matrix_chars)
            
            for row in range(logo_height - 1, 0, -1):
                matrix[row][col] = matrix[row-1][col]
            
            if matrix[0][col] != ' ':
                matrix[0][col] = random.choice(matrix_chars)
        
        # Print matrix with logo overlay
        for row in range(logo_height):
            line = ''
            for col in range(logo_width):
                if col < len(logo_frames[row]) and logo_frames[row][col] != ' ':
                    char = logo_frames[row][col]
                    # Gradually change from purple to blue
                    color = (
                        int(147 + (0 - 147) * frame / 49),  # R
                        int(112 + (191 - 112) * frame / 49), # G
                        int(219 + (255 - 219) * frame / 49)  # B
                    )
                else:
                    char = matrix[row][col]
                    # Random blue or purple for falling characters
                    if random.random() < 0.5:
                        color = (147, 112, 219)  # Medium Purple
                    else:
                        color = (0, 191, 255)  # Deep Sky Blue
                line += gradient_text(char, color, color)
            print(line)
        
        await asyncio.sleep(0.1)

async def main():
    logo_frames = [
        "  _____  ___   _      __ __  ____  _____  __ __ ",
        " / ___/ /   \\ | T    |  T  Tl    j|     ||  T  T",
        "(   \\_ Y     Y| |    |  |  | |  T |   __j|  |  |",
        " \\__  T|  O  || l___ |  |  | |  | |  l_  |  ~  |",
        " /  \\ ||     ||     T|  :  | |  | |   _] l___, |",
        " \\    |l     !|     |l     | j  l |  T   |     !",
        "  \\___j \\___/ l_____j \\__,_j|____jl__j   l____/ "
    ]

    copypaste_art = [
        "   ___                          ___              _         ",
        "  / __\\  ___   _ __   _   _    / _ \\  __ _  ___ | |_   ___ ",
        " / /    / _ \\ | '_ \\ | | | |  / /_)/ / _` |/ __|| __| / _ \\",
        "/ /___ | (_) || |_) || |_| | / ___/ | (_| |\\__ \\| |_ |  __/",
        "\\____/  \\___/ | .__/  \\__, | \\/      \\__,_||___/ \\__| \\___|",
        "              |_|     |___/                                "
    ]

    combined_art = logo_frames + [""] + copypaste_art

    # Display both logos together using matrix effect
    await matrix_effect(combined_art)

    # Final display of both logos
    print("\033[H\033[J", end="")  # Clear screen
    for line in combined_art:
        print(gradient_text(line, MAIN_COLOR_START, MAIN_COLOR_END))

    intro_text = gradient_text("""
Welcome to the Soluify Telegram Copy & Paste Bot!
====================================================
1. Log in with your API details (securely, of course!)
2. List all your Telegram chat IDs. (Note your source and destination IDs)
3. Set up the bot with the provided prompts.
4. Add custom filters and signatures to your messages.
5. Sit back and let us handle the rest!
""", MAIN_COLOR_START, MAIN_COLOR_END)

    print(intro_text)

    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        print(gradient_text("Let's set up your Telegram API credentials!", MAIN_COLOR_START, MAIN_COLOR_END, "🚀"))
        credentials_saved = store_credentials()
        api_id, api_hash, phone_number = read_credentials()
    else:
        credentials_saved = True

    client = TelegramClient('session_' + phone_number, api_id, api_hash)
    forwarder = TelegramForwarder(client, phone_number)

    while True:
        print(gradient_text("\nWhat's your mission for today?", MAIN_COLOR_START, MAIN_COLOR_END, "🕵️"))
        print(gradient_text("1. List My Chat IDs", PROMPT_COLOR_START, PROMPT_COLOR_END, "📋"))
        print(gradient_text("2. Set Up Message Forwarding", PROMPT_COLOR_START, PROMPT_COLOR_END, "⚙️"))
        print(gradient_text("3. Edit Profile", PROMPT_COLOR_START, PROMPT_COLOR_END, "✏️"))
        print(gradient_text("4. Help", PROMPT_COLOR_START, PROMPT_COLOR_END, "❓"))
        print(gradient_text("5. Exit", PROMPT_COLOR_START, PROMPT_COLOR_END, "👋"))
        
        choice = input(gradient_text("Pick your adventure (1-5): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        
        try:
            if choice == "1":
                await animated_transition("Unveiling your chat universe")
                await forwarder.list_chats()
            elif choice == "2":
                profiles = load_profiles()
                if profiles:
                    use_profile = input(gradient_text("Do you want to use a saved profile? (y/n): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
                    if use_profile.lower() == 'y':
                        print(gradient_text("Available profiles:", MAIN_COLOR_START, MAIN_COLOR_END, "🎭"))
                        for idx, profile_name in enumerate(profiles):
                            print(gradient_text(f"{idx + 1}. {profile_name}", MAIN_COLOR_START, MAIN_COLOR_END))
                        profile_idx = int(input(gradient_text("Enter the profile number: ", PROMPT_COLOR_START, PROMPT_COLOR_END))) - 1
                        profile_name = list(profiles.keys())[profile_idx]
                        config = profiles[profile_name]
                        source_chat_ids = config['source_chat_ids']
                        destination_channel_ids = config['destination_channel_ids']
                        keywords = config['keywords']
                        signature = config['signature']
                        blacklist = config['blacklist']
                    else:
                        source_chat_ids, destination_channel_ids, keywords, signature, blacklist = get_new_config()
                else:
                    source_chat_ids, destination_channel_ids, keywords, signature, blacklist = get_new_config()
                
                await animated_transition("Preparing the message wormhole")
                await forwarder.forward_messages_to_channels(source_chat_ids, destination_channel_ids, keywords, signature)
            elif choice == "3":
                profiles = load_profiles()
                if profiles:
                    print(gradient_text("Available profiles:", MAIN_COLOR_START, MAIN_COLOR_END, "🎭"))
                    for idx, profile_name in enumerate(profiles):
                        print(gradient_text(f"{idx + 1}. {profile_name}", MAIN_COLOR_START, MAIN_COLOR_END))
                    profile_idx = int(input(gradient_text("Enter the profile number to edit: ", PROMPT_COLOR_START, PROMPT_COLOR_END))) - 1
                    profile_name = list(profiles.keys())[profile_idx]
                    edit_profile(profile_name)
                else:
                    print(gradient_text("No profiles found. Create a new profile in 'Set Up Message Forwarding'.", ALERT_COLOR, ALERT_COLOR))
            elif choice == "4":
                await display_help()
            elif choice == "5":
                await graceful_shutdown(credentials_saved, phone_number)
                break
            else:
                print(gradient_text("Oops! That's not on the menu. Let's try again!", ALERT_COLOR, ALERT_COLOR, "❌"))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(gradient_text(f"Unexpected twist in our adventure: {e}. Let's regroup and try again!", ALERT_COLOR, ALERT_COLOR))
            await asyncio.sleep(5)  # Wait for a few seconds before retrying

def get_new_config():
    source_chat_ids = input(gradient_text("Enter the source chat IDs (comma separated): ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    source_chat_ids = [int(chat_id.strip()) for chat_id in source_chat_ids]
    destination_channel_ids = input(gradient_text("Enter the destination chat IDs (comma separated): ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    destination_channel_ids = [int(chat_id.strip()) for chat_id in destination_channel_ids]
    keywords = input(gradient_text("Enter keywords to filter messages (optional). Leave blank to forward all messages: ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    keywords = [keyword.strip() for keyword in keywords if keyword.strip()]
    signature = input(gradient_text("Enter the signature to append to each message: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    blacklist = input(gradient_text("Enter blacklisted words (comma separated, or leave blank): ", PROMPT_COLOR_START, PROMPT_COLOR_END)).split(',')
    blacklist = [word.strip().lower() for word in blacklist if word.strip()]
    save_choice = input(gradient_text("Do you want to save this configuration as a profile? (y/n): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    if save_choice.lower() == 'y':
        profile_name = input(gradient_text("Enter a name for this profile: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        save_profile(profile_name, {
            'source_chat_ids': source_chat_ids,
            'destination_channel_ids': destination_channel_ids,
            'keywords': keywords,
            'signature': signature,
            'blacklist': blacklist
        })
    return source_chat_ids, destination_channel_ids, keywords, signature, blacklist

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())