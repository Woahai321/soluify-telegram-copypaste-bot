import time
import asyncio
import re
import random
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from colorama import init, Fore, Style
from termcolor import colored
import sys

init(autoreset=True)

def animate_text(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

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

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)
        self.username_replacements = {}

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
        for dialog in dialogs:
            print(gradient_text(f"Chat ID: {dialog.id}, Title: {dialog.title}", (0, 255, 255), (0, 128, 128)))
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")
        
        animate_text(gradient_text("All your chats are listed! 📜", (0, 255, 0), (0, 128, 0)))

    async def forward_messages_to_channel(self, source_chat_ids, destination_channel_id, keywords, signature):
        await self.client.connect()

        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input(gradient_text('Enter the code: ', (255, 255, 0), (255, 165, 0))))
            except SessionPasswordNeededError:
                await self.client.sign_in(password=input(gradient_text('Two step verification is enabled. Please enter your password: ', (255, 255, 0), (255, 165, 0))))

        last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

        while True:
            animate_text(gradient_text("👀 Soluify is on the lookout for new messages...", (0, 191, 255), (30, 144, 255)))
            for chat_id in source_chat_ids:
                messages = await self.client.get_messages(chat_id, min_id=last_message_ids[chat_id], limit=None)

                for message in reversed(messages):
                    should_forward = False
                    if keywords:
                        if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
                            should_forward = True
                    else:
                        should_forward = True

                    if should_forward:
                        if message.text:
                            forwarded_text = self.replace_usernames(message.text)
                            await self.client.send_message(destination_channel_id, f"{forwarded_text}\n\n**{signature}**")
                        if message.media:
                            await self.client.send_file(destination_channel_id, message.media, caption=f"{message.text}\n\n**{signature}**" if message.text else f"**{signature}**")
                        
                        animate_text(gradient_text("✅ Message forwarded with your signature!", (0, 255, 0), (0, 128, 0)))

                    last_message_ids[chat_id] = max(last_message_ids[chat_id], message.id)

            await asyncio.sleep(5)

    def replace_usernames(self, text):
        for username, replacement in self.username_replacements.items():
            text = re.sub(f'@{username}', replacement, text)
        return text

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

async def main():
    logo_frames = [
        "     ___       _       _  ___     ",
        "    / __> ___ | | _ _ <_>| | '_ _ ",
        "    \__ \/ . \| || | || || |-| | |",
        "    <___/\___/|_|`___||_||_| `_. |",
        "                             <___'"
    ]

    colors = [
        (255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0),
        (0, 0, 255), (75, 0, 130), (238, 130, 238)
    ]

    async def rainbow_effect():
        for _ in range(10):
            print("\033[H\033[J", end="")
            for i, line in enumerate(logo_frames):
                color = colors[i % len(colors)]
                print(gradient_text(line, color, (255, 255, 255)))
            await asyncio.sleep(0.1)
            colors.append(colors.pop(0))

    async def typing_effect():
        for i in range(len(logo_frames)):
            print("\033[H\033[J", end="")
            for j in range(i + 1):
                color = random.choice(colors)
                print(gradient_text(logo_frames[j], color, (255, 255, 255)))
            await asyncio.sleep(0.2)

    async def glitch_effect():
        for _ in range(5):
            print("\033[H\033[J", end="")
            for line in logo_frames:
                glitched_line = ''.join(random.choice(['_', '/', '\\', '|', ' ']) if random.random() < 0.1 else c for c in line)
                print(gradient_text(glitched_line, random.choice(colors), (255, 255, 255)))
            await asyncio.sleep(0.1)

    # Main animation sequence
    for _ in range(2):
        await typing_effect()
        await asyncio.sleep(0.5)
        await rainbow_effect()
        await asyncio.sleep(0.5)
        await glitch_effect()
        await asyncio.sleep(0.5)

    # Final display
    print("\033[H\033[J", end="")
    for line in logo_frames:
        print(gradient_text(line, (0, 191, 255), (30, 144, 255)))

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
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_ids = input(gradient_text("Enter the source chat IDs (comma separated): ", (0, 191, 255), (30, 144, 255))).split(',')
        source_chat_ids = [int(chat_id.strip()) for chat_id in source_chat_ids]
        destination_channel_id = int(input(gradient_text("Enter the destination chat ID: ", (0, 191, 255), (30, 144, 255))))
        print(gradient_text("Enter keywords to filter messages (optional). Leave blank to forward all messages.", (0, 255, 255), (0, 128, 128)))
        keywords = input(gradient_text("Keywords (comma separated if multiple, or leave blank): ", (0, 191, 255), (30, 144, 255))).split(',')
        signature = input(gradient_text("Enter the signature to append to each message: ", (0, 191, 255), (30, 144, 255)))
        
        replace_usernames = input(gradient_text("Do you want to replace usernames in forwarded messages? (y/n): ", (0, 191, 255), (30, 144, 255))).lower() == 'y'
        if replace_usernames:
            while True:
                username = input(gradient_text("Enter a username to replace (without @, or press Enter to finish): ", (0, 191, 255), (30, 144, 255)))
                if not username:
                    break
                replacement = input(gradient_text(f"Enter replacement for @{username}: ", (0, 191, 255), (30, 144, 255)))
                forwarder.username_replacements[username] = replacement
        
        await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords, signature)
    else:
        print(gradient_text("❌ Oops! That's not a valid choice.", (255, 0, 0), (255, 100, 100)))

if __name__ == "__main__":
    asyncio.run(main())