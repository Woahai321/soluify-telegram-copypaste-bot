import asyncio
import random
import re
import sys
import time
import json
import signal
import logging
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError, RPCError, ChatForwardsRestrictedError
from colorama import init, Fore, Style
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm

init(autoreset=True)

# Define color schemes
MAIN_COLOR_START = (147, 112, 219)  # Medium Purple
MAIN_COLOR_END = (0, 191, 255)      # Deep Sky Blue
ALERT_COLOR = (255, 69, 0)          # Red-Orange
SUCCESS_COLOR = (50, 205, 50)       # Lime Green
PROMPT_COLOR_START = (0, 255, 255)  # Cyan
PROMPT_COLOR_END = (135, 206, 250)  # Light Sky Blue

CONFIG_FILE = 'telegramconfiguration.json'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gradient_text(text, start_color, end_color):
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    gradient = []
    length = len(text)
    for i, char in enumerate(text):
        r = start_r + (end_r - start_r) * i / length
        g = start_g + (end_g - start_g) * i / length
        b = start_b + (end_b - start_b) * i / length
        gradient.append(f"\033[38;2;{int(r)};{int(g)};{int(b)}m{char}\033[0m")
    return ''.join(gradient)

async def animated_transition(text, duration=0.5):
    colors = [MAIN_COLOR_START, MAIN_COLOR_END]
    emojis = ["✨", "🚀", "💫", "🌟", "💡", "🔮", "🎉"]
    for _ in range(int(duration * 10)):
        color = random.choice(colors)
        emoji = random.choice(emojis)
        print(f"\r{gradient_text(f'{emoji} {text} {emoji}', color, color)}", end="", flush=True)
        await asyncio.sleep(0.05)
    print()

class TelegramForwarder:
    def __init__(self, client, phone_number):
        self.client = client
        self.phone_number = phone_number
        self.blacklist = []

    async def list_chats(self):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input(gradient_text('Enter the code: ', PROMPT_COLOR_START, PROMPT_COLOR_END)))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input(gradient_text('Two step verification is enabled. Please enter your password: ', PROMPT_COLOR_START, PROMPT_COLOR_END)))

        dialogs = await self.client.get_dialogs()
        
        with open(f"chats_of_{self.phone_number}.txt", "w") as chats_file, tqdm(total=len(dialogs), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=75, colour="blue") as pbar:
            for dialog in dialogs:
                chat_info = f"Chat ID: {dialog.id}, Title: {dialog.title}"
                print(gradient_text(chat_info, MAIN_COLOR_START, MAIN_COLOR_END))
                chats_file.write(chat_info + "\n")
                pbar.update(1)
        
        print(gradient_text("All your chats are listed! 📜", SUCCESS_COLOR, SUCCESS_COLOR))

    async def forward_messages_to_channels(self, source_chat_ids, destination_channel_ids, keywords, signature):
        try:
            await self.client.connect()

            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone_number)
                try:
                    await self.client.sign_in(self.phone_number, input(gradient_text('Enter the code: ', PROMPT_COLOR_START, PROMPT_COLOR_END)))
                except SessionPasswordNeededError:
                    await self.client.sign_in(password=input(gradient_text('Two step verification is enabled. Please enter your password: ', PROMPT_COLOR_START, PROMPT_COLOR_END)))

            last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

            while True:
                print(gradient_text("👀 Soluify is on the lookout for new messages...", MAIN_COLOR_START, MAIN_COLOR_END))
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
                        
                        print(gradient_text("✅ Message forwarded with your signature!", SUCCESS_COLOR, SUCCESS_COLOR))

                        last_message_ids[chat_id] = max(last_message_ids[chat_id], message.id)

                await asyncio.sleep(5)
        except FloodWaitError as e:
            logger.error(gradient_text(f"Flood wait error: {e}. Waiting for {e.seconds} seconds before retrying.", ALERT_COLOR, ALERT_COLOR))
            await asyncio.sleep(e.seconds)
            await self.forward_messages_to_channels(source_chat_ids, destination_channel_ids, keywords, signature)
        except RPCError as e:
            logger.error(gradient_text(f"RPC error: {e}. Please check your network connection and try again.", ALERT_COLOR, ALERT_COLOR))
        except Exception as e:
            logger.error(gradient_text(f"An unexpected error occurred: {e}", ALERT_COLOR, ALERT_COLOR))

def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print(gradient_text("Couldn't find the credentials file. If this is running for the first time, please log in below:", ALERT_COLOR, ALERT_COLOR))
        return None, None, None

def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

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

async def graceful_shutdown(signum, frame):
    logger.info(gradient_text("Bot shutting down gracefully...", SUCCESS_COLOR, SUCCESS_COLOR))
    await asyncio.sleep(1)
    exit(0)

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

    total_height = len(logo_frames) + len(copypaste_art) + 1  # +1 for separation
    logo_width = max(len(line) for line in logo_frames)
    copypaste_width = max(len(line) for line in copypaste_art)
    total_width = max(logo_width, copypaste_width)

    # Combine both logos into a single list
    combined_art = logo_frames + [""] + copypaste_art

    # Display both logos together using matrix effect
    await matrix_effect(combined_art)

    # Final display of both logos
    print("\033[H\033[J", end="")  # Clear screen
    for line in combined_art:
        print(gradient_text(line, MAIN_COLOR_START, MAIN_COLOR_END))

    intro_text = gradient_text("""
👋 Welcome to the Soluify Telegram Copy & Paste Bot!
====================================================
1. Log in with your API details.
2. List all your Telegram chat IDs. (Note your source and destination IDs)
3. Set up the bot with the provided prompts.
4. Add custom filters and signatures to your messages.
5. Sit back and let us handle the rest! 🧘
""", MAIN_COLOR_START, MAIN_COLOR_END)

    print(intro_text)

    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        api_id = input(gradient_text("Please enter your API ID: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        api_hash = input(gradient_text("Please enter your API Hash: ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        phone_number = input(gradient_text("Please enter your phone number (e.g., 447123456789): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        write_credentials(api_id, api_hash, phone_number)

    client = TelegramClient('session_' + phone_number, api_id, api_hash)
    forwarder = TelegramForwarder(client, phone_number)

    profiles = load_profiles()
    if profiles:
        print(gradient_text("Available profiles:", MAIN_COLOR_START, MAIN_COLOR_END))
        for idx, profile_name in enumerate(profiles):
            print(gradient_text(f"{idx + 1}. {profile_name}", MAIN_COLOR_START, MAIN_COLOR_END))
        choice = input(gradient_text("Do you want to use a profile? (y/n): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        if choice.lower() == 'y':
            profile_idx = int(input(gradient_text("Enter the profile number: ", PROMPT_COLOR_START, PROMPT_COLOR_END))) - 1
            profile_name = list(profiles.keys())[profile_idx]
            config = profiles[profile_name]
            source_chat_ids = config['source_chat_ids']
            destination_channel_ids = config['destination_channel_ids']
            keywords = config['keywords']
            signature = config['signature']
            blacklist = config['blacklist']
        else:
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
    else:
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

    signal.signal(signal.SIGINT, lambda signum, frame: asyncio.create_task(graceful_shutdown(signum, frame)))
    signal.signal(signal.SIGTERM, lambda signum, frame: asyncio.create_task(graceful_shutdown(signum, frame)))

    print(gradient_text("What do you want to do?", MAIN_COLOR_START, MAIN_COLOR_END))
    print(gradient_text("1. List My Chat IDs 📋", PROMPT_COLOR_START, PROMPT_COLOR_END))
    print(gradient_text("2. Set Up Message Forwarding ⚙️", PROMPT_COLOR_START, PROMPT_COLOR_END))
    
    choice = input(gradient_text("Pick an option (1 or 2): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
    
    while True:
        try:
            if choice == "1":
                await animated_transition("Listing chats")
                await forwarder.list_chats()
                break
            elif choice == "2":
                await animated_transition("Setting up message forwarding")
                await forwarder.forward_messages_to_channels(source_chat_ids, destination_channel_ids, keywords, signature)
                break
            else:
                print(gradient_text("❌ Oops! That's not a valid choice.", ALERT_COLOR, ALERT_COLOR))
                choice = input(gradient_text("Pick an option (1 or 2): ", PROMPT_COLOR_START, PROMPT_COLOR_END))
        except Exception as e:
            logger.error(gradient_text(f"An error occurred: {e}. Restarting the selected option...", ALERT_COLOR, ALERT_COLOR))
            await asyncio.sleep(5)  # Wait for a few seconds before retrying

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())