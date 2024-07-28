# ==============================================================================
# Soluify  |  Your #1 IT Problem Solver  |  {telegram-copypaste-bot v1.0}
# ==============================================================================
#  __         _   
# (_  _ |   .(_   
# __)(_)||_||| \/ 
#              /
# © 2024 Soluify LLC
# ------------------------------------------------------------------------------
import time
import asyncio
import re
import random
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageEntityMention
from colorama import init, Fore, Style
import sys
from tqdm import tqdm
from tqdm.asyncio import tqdm as atqdm

init(autoreset=True)

def gradient_text(text, start_color, end_color):
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    gradient = []
    for i, char in enumerate(text):
        r = start_r + (end_r - start_r) * i // len(text)
        g = start_g + (end_g - start_g) * i // len(text)
        b = start_b + (end_b - start_b) * i // len(text)
        gradient.append(f"\033[38;2;{r};{g};{b}m{char}\033[0m")
    return ''.join(gradient)

async def animated_transition(text, duration=0.5):
    colors = [(255,0,0), (255,165,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (238,130,238)]
    emojis = ["✨", "🚀", "💫", "🌟", "💡", "🔮", "🎉"]
    for _ in range(int(duration * 10)):
        color = random.choice(colors)
        emoji = random.choice(emojis)
        print(f"\r{gradient_text(f'{emoji} {text} {emoji}', color, color)}", end="", flush=True)
        await asyncio.sleep(0.05)
    print()

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)
        self.username_replacement = None
        self.blacklist = []

    async def list_chats(self):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input(gradient_text('Enter the code: ', (255, 255, 0), (255, 165, 0))))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input(gradient_text('Two step verification is enabled. Please enter your password: ', (255, 255, 0), (255, 165, 0))))

        dialogs = await self.client.get_dialogs()
        chats_file = open(f"chats_of_{self.phone_number}.txt", "w")
        
        with tqdm(total=len(dialogs), bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=75, colour="blue") as pbar:
            for dialog in dialogs:
                chat_info = f"Chat ID: {dialog.id}, Title: {dialog.title}"
                print(gradient_text(chat_info, (0, 255, 255), (0, 128, 128)))
                chats_file.write(chat_info + "\n")
                pbar.update(1)
        chats_file.close()
        
        print(gradient_text("All your chats are listed! 📜", (0, 255, 0), (0, 128, 0)))

    async def forward_messages_to_channels(self, source_chat_ids, destination_channel_ids, keywords, signature):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input(gradient_text('Enter the code: ', (255, 255, 0), (255, 165, 0))))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input(gradient_text('Two step verification is enabled. Please enter your password: ', (255, 255, 0), (255, 165, 0))))

        last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

        while True:
            print(gradient_text("👀 Soluify is on the lookout for new messages...", (0, 191, 255), (30, 144, 255)))
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
                            forwarded_text = await self.replace_usernames(message)
                            for dest_id in destination_channel_ids:
                                await self.client.send_message(dest_id, forwarded_text.text + f"\n\n**{signature}**")
                        if message.media:
                            for dest_id in destination_channel_ids:
                                await self.client.send_file(dest_id, message.media, caption=f"{message.text}\n\n**{signature}**" if message.text else f"**{signature}**")
                        
                        print(gradient_text("✅ Message forwarded with your signature!", (0, 255, 0), (0, 128, 0)))

                    last_message_ids[chat_id] = max(last_message_ids[chat_id], message.id)

            await asyncio.sleep(5)

    async def replace_usernames(self, message):
        if self.username_replacement:
            new_text = message.text
            new_entities = []
            offset_change = 0

            for entity in message.entities or []:
                if isinstance(entity, MessageEntityMention):
                    start = entity.offset + offset_change
                    end = start + entity.length
                    old_username = new_text[start+1:end]  # +1 to skip the '@'
                    new_text = new_text[:start] + self.username_replacement + new_text[end:]
                    
                    new_entity = MessageEntityMention(
                        offset=start,
                        length=len(self.username_replacement)
                    )
                    new_entities.append(new_entity)
                    
                    offset_change += len(self.username_replacement) - entity.length
                else:
                    entity.offset += offset_change
                    new_entities.append(entity)

            message.text = new_text
            message.entities = new_entities

        return message

def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print(gradient_text("Couldn't find the credentials file. If this is running for the first time, please log in below:", (255, 0, 0), (255, 100, 100)))
        return None, None, None

def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

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
                if logo_frames[row][col] != ' ':
                    char = logo_frames[row][col]
                    # Gradually change from purple to blue
                    color = (
                        int(75 + (0 - 75) * frame / 49),  # R
                        int(0 + (191 - 0) * frame / 49),  # G
                        int(130 + (255 - 130) * frame / 49)  # B
                    )
                else:
                    char = matrix[row][col]
                    # Random blue or purple for falling characters
                    if random.random() < 0.5:
                        color = (75, 0, 130)  # Purple
                    else:
                        color = (0, 0, 255)  # Blue
                line += gradient_text(char, color, color)
            print(line)
        
        await asyncio.sleep(0.1)

async def pixelate_effect(text, frames=10):
    lines = text.split('\n')
    max_length = max(len(line) for line in lines)
    
    for frame in range(frames):
        clear_percentage = frame / frames
        pixelated = []
        for line in lines:
            new_line = ''
            for char in line.ljust(max_length):
                if random.random() < clear_percentage:
                    new_line += char
                else:
                    new_line += random.choice('░▒▓█')
            pixelated.append(new_line)
        
        print("\033[H\033[J", end="")  # Clear screen
        for line in pixelated:
            print(gradient_text(line, (75, 0, 130), (0, 191, 255)))
        await asyncio.sleep(0.1)

async def main():
    logo_frames = [
        "     ___       _       _  ___     ",
        "    / __> ___ | | _ _ <_>| | '_ _ ",
        "    \__ \/ . \| || | || || |-| | |",
        "    <___/\___/|_|`___||_||_| `_. |",
        "                             <___'"
    ]

    copypaste_art = """
 __   __   __       __        __  ___  ___ 
/  ` /  \ |__) \ / |__)  /\  /__`  |  |__  
\__, \__/ |     |  |    /~~\ .__/  |  |___ 
                                           
    """

    total_height = len(logo_frames) + len(copypaste_art.split('\n')) + 1  # +1 for separation
    logo_width = max(len(line) for line in logo_frames)
    copypaste_width = max(len(line) for line in copypaste_art.split('\n'))
    total_width = max(logo_width, copypaste_width)

    async def matrix_effect():
        matrix = [[' ' for _ in range(logo_width)] for _ in range(len(logo_frames))]
        matrix_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,.<>?"
        
        for frame in atqdm(range(50), desc="Loading", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=75, colour="magenta"):
            print("\033[H\033[J", end="")  # Clear screen
            
            # Update matrix
            for col in range(logo_width):
                if random.random() < 0.2:  # Chance to start a new "drop"
                    matrix[0][col] = random.choice(matrix_chars)
                
                for row in range(len(logo_frames) - 1, 0, -1):
                    matrix[row][col] = matrix[row-1][col]
                
                if matrix[0][col] != ' ':
                    matrix[0][col] = random.choice(matrix_chars)
            
            # Print matrix with logo overlay
            for row in range(len(logo_frames)):
                line = ''
                for col in range(logo_width):
                    if logo_frames[row][col] != ' ':
                        char = logo_frames[row][col]
                        color = (
                            int(75 + (0 - 75) * frame / 49),  # R
                            int(0 + (191 - 0) * frame / 49),  # G
                            int(130 + (255 - 130) * frame / 49)  # B
                        )
                    else:
                        char = matrix[row][col]
                        color = (0, 0, 255)  # Blue for matrix
                    line += gradient_text(char, color, color)
                print(line)
            
            # Print copypaste art with pixelate effect
            print()  # Separation line
            copypaste_lines = copypaste_art.split('\n')
            clear_percentage = frame / 49
            for line in copypaste_lines:
                pixelated_line = ''
                for char in line:
                    if random.random() < clear_percentage:
                        pixelated_line += char
                    else:
                        pixelated_line += random.choice('░▒▓█')
                print(gradient_text(pixelated_line, (0, 0, 255), (0, 191, 255)))  # Blue gradient for copypaste
            
            await asyncio.sleep(0.1)

    await matrix_effect()

    # Final display of both logos
    print("\033[H\033[J", end="")  # Clear screen
    for line in logo_frames:
        print(gradient_text(line, (0, 191, 255), (0, 191, 255)))  # Deep Sky Blue color for Soluify
    print()  # Add a blank line for separation
    for line in copypaste_art.split('\n'):
        print(gradient_text(line, (0, 191, 255), (0, 191, 255)))  # Deep Sky Blue color for COPYPASTE

    intro_text = gradient_text("""
👋 Welcome to the Soluify Telegram Copy & Paste Bot!
====================================================
1. Log in with your API details.
2. List all your Telegram chat IDs. (Note your source and destination IDs)
3. Set up the bot with the provided prompts.
4. Add custom filters and signatures to your messages.
5. Sit back and let us handle the rest! 🧘
""", (255, 0, 255), (0, 255, 255))

    print(intro_text)

    api_id, api_hash, phone_number = read_credentials()

    if api_id is None or api_hash is None or phone_number is None:
        api_id = input(gradient_text("Please enter your API ID: ", (0, 191, 255), (30, 144, 255)))
        api_hash = input(gradient_text("Please enter your API Hash: ", (0, 191, 255), (30, 144, 255)))
        phone_number = input(gradient_text("Please enter your phone number (e.g., 447123456789): ", (0, 191, 255), (30, 144, 255)))
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print(gradient_text("What do you want to do?", (0, 255, 255), (0, 128, 128)))
    print(gradient_text("1. List My Chat IDs 📋", (0, 191, 255), (30, 144, 255)))
    print(gradient_text("2. Set Up Message Forwarding ⚙️", (0, 191, 255), (30, 144, 255)))
    
    choice = input(gradient_text("Pick an option (1 or 2): ", (255, 255, 0), (255, 165, 0)))
    
    if choice == "1":
        await animated_transition("Listing chats")
        await forwarder.list_chats()
    elif choice == "2":
        await animated_transition("Setting up message forwarding")
        source_chat_ids = input(gradient_text("Enter the source chat IDs (comma separated): ", (0, 191, 255), (30, 144, 255))).split(',')
        source_chat_ids = [int(chat_id.strip()) for chat_id in source_chat_ids]
        
        destination_channel_ids = input(gradient_text("Enter the destination chat IDs (comma separated): ", (0, 191, 255), (30, 144, 255))).split(',')
        destination_channel_ids = [int(chat_id.strip()) for chat_id in destination_channel_ids]
        
        print(gradient_text("Enter keywords to filter messages (optional). Leave blank to forward all messages.", (0, 255, 255), (0, 128, 128)))
        keywords = input(gradient_text("Keywords (comma separated if multiple, or leave blank): ", (0, 191, 255), (30, 144, 255))).split(',')
        keywords = [keyword.strip() for keyword in keywords if keyword.strip()]
        
        signature = input(gradient_text("Enter the signature to append to each message: ", (0, 191, 255), (30, 144, 255)))
        
        replace_usernames = input(gradient_text("Do you want to replace all @usernames in forwarded messages? (y/n): ", (0, 191, 255), (30, 144, 255))).lower() == 'y'
        if replace_usernames:
            replacement = input(gradient_text("Enter the replacement for all @usernames: ", (0, 191, 255), (30, 144, 255)))
            forwarder.username_replacement = replacement
        
        blacklist = input(gradient_text("Enter blacklisted words (comma separated, or leave blank): ", (0, 191, 255), (30, 144, 255))).split(',')
        forwarder.blacklist = [word.strip().lower() for word in blacklist if word.strip()]
        
        await animated_transition("Starting message forwarding")
        await forwarder.forward_messages_to_channels(source_chat_ids, destination_channel_ids, keywords, signature)
    else:
        print(gradient_text("❌ Oops! That's not a valid choice.", (255, 0, 0), (255, 100, 100)))

if __name__ == "__main__":
    asyncio.run(main())