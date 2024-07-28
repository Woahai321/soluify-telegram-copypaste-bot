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
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from colorama import init, Fore, Style
from pyfiglet import Figlet

init(autoreset=True)

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def list_chats(self):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input(Fore.YELLOW + 'Enter the code: ' + Style.RESET_ALL))

        # Get a list of all the dialogs (chats)
        dialogs = await self.client.get_dialogs()
        chats_file = open(f"chats_of_{self.phone_number}.txt", "w")
        # Print information about each chat
        for dialog in dialogs:
            print(Fore.CYAN + f"Chat ID: {dialog.id}, Title: {dialog.title}")
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")
          
        print(Fore.GREEN + "All your chats are listed! 📜")

    async def forward_messages_to_channel(self, source_chat_ids, destination_channel_id, keywords, signature):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input(Fore.YELLOW + 'Enter the code: ' + Style.RESET_ALL))

        last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

        while True:
            print(Fore.CYAN + "👀 Soluify is on the lookout for new messages...")
            for chat_id in source_chat_ids:
                # Get new messages since the last checked message
                messages = await self.client.get_messages(chat_id, min_id=last_message_ids[chat_id], limit=None)

                for message in reversed(messages):
                    # Check if the message text includes any of the keywords
                    if keywords:
                        if message.text and any(keyword in message.text.lower() for keyword in keywords):
                            print(Fore.YELLOW + f"🔎 Found a keyword in message: {message.text}")

                            # Forward the message to the destination channel with the signature
                            await self.client.send_message(destination_channel_id, f"{message.text}\n\n**{signature}**")

                            print(Fore.GREEN + "✅ Message sent with your signature!")
                    else:
                            # Forward the message to the destination channel with the signature
                            await self.client.send_message(destination_channel_id, f"{message.text}\n\n**{signature}**")

                            print(Fore.GREEN + "✅ Message sent with your signature!")

                    # Update the last message ID
                    last_message_ids[chat_id] = max(last_message_ids[chat_id], message.id)

            # Add a delay before checking for new messages again
            await asyncio.sleep(5)  # Adjust the delay time as needed


# Function to read credentials from file
def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print(Fore.RED + "Couldn't find the credentials file, if this is running for first time, please log in below:")
        return None, None, None

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    # Display ASCII Art Logo
    logo = """
     ___       _       _  ___     
    / __> ___ | | _ _ <_>| | '_ _ 
    \__ \/ . \| || | || || |-| | |
    <___/\___/|_|`___||_||_| `_. |
                             <___'
    """
    print(Fore.LIGHTBLUE_EX + logo)

    # Introductory Text
    intro_text = Fore.LIGHTMAGENTA_EX + """
👋 Welcome to the Soluify Telegram Copy & Paste Bot!
====================================================
1. Log in with your API details.
2. List all your Telegram chat IDs. (Note your source and destination IDs)
3. Set up the bot with the provided prompts.
4. Add custom filters and signatures to your messages.
5. Sit back and let us handle the rest! 🧘
"""

    print(intro_text)

    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input(Fore.LIGHTBLUE_EX + "Please enter your API ID: " + Style.RESET_ALL)
        api_hash = input(Fore.LIGHTBLUE_EX + "Please enter your API Hash: " + Style.RESET_ALL)
        phone_number = input(Fore.LIGHTBLUE_EX + "Please enter your phone number (e.g., 447123456789): " + Style.RESET_ALL)
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print(Fore.CYAN + "What do you want to do?")
    print(Fore.CYAN + "1. List My Chat IDs 📋")
    print(Fore.CYAN + "2. Set Up Message Forwarding ⚙️")
    
    choice = input(Fore.LIGHTBLUE_EX + "Pick an option (1 or 2): " + Style.RESET_ALL)
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_ids = input(Fore.LIGHTBLUE_EX + "Enter the source chat IDs (comma separated): " + Style.RESET_ALL).split(',')
        source_chat_ids = [int(chat_id.strip()) for chat_id in source_chat_ids]
        destination_channel_id = int(input(Fore.LIGHTBLUE_EX + "Enter the destination chat ID: " + Style.RESET_ALL))
        print(Fore.CYAN + "Enter keywords to filter messages (optional). Leave blank to forward all messages.")
        keywords = input(Fore.LIGHTBLUE_EX + "Keywords (comma separated if multiple, or leave blank): " + Style.RESET_ALL).split(',')
        signature = input(Fore.LIGHTBLUE_EX + "Enter the signature to append to each message: " + Style.RESET_ALL)
        
        await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords, signature)
    else:
        print(Fore.RED + "❌ Oops! That's not a valid choice.")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())