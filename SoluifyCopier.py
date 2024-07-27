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
          
        print(Fore.GREEN + "List of groups printed successfully!")

    async def forward_messages_to_channel(self, source_chat_ids, destination_channel_id, keywords):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input(Fore.YELLOW + 'Enter the code: ' + Style.RESET_ALL))

        last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

        while True:
            print(Fore.CYAN + "Checking for messages and forwarding them...")
            for chat_id in source_chat_ids:
                # Get new messages since the last checked message
                messages = await self.client.get_messages(chat_id, min_id=last_message_ids[chat_id], limit=None)

                for message in reversed(messages):
                    # Check if the message text includes any of the keywords
                    if keywords:
                        if message.text and any(keyword in message.text.lower() for keyword in keywords):
                            print(Fore.YELLOW + f"Message contains a keyword: {message.text}")

                            # Forward the message to the destination channel
                            await self.client.send_message(destination_channel_id, message.text)

                            print(Fore.GREEN + "Message forwarded")
                    else:
                            # Forward the message to the destination channel
                            await self.client.send_message(destination_channel_id, message.text)

                            print(Fore.GREEN + "Message forwarded")

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
        print(Fore.RED + "Credentials file not found.")
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

    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input(Fore.LIGHTBLUE_EX + "Enter your API ID: " + Style.RESET_ALL)
        api_hash = input(Fore.LIGHTBLUE_EX + "Enter your API Hash: " + Style.RESET_ALL)
        phone_number = input(Fore.LIGHTBLUE_EX + "Enter your phone number: " + Style.RESET_ALL)
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print(Fore.CYAN + "Choose an option:")
    print(Fore.CYAN + "1. List My Chat IDs")
    print(Fore.CYAN + "2. Configure Forwarding Messages")
    
    choice = input(Fore.LIGHTBLUE_EX + "Enter your choice: " + Style.RESET_ALL)
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        source_chat_ids = input(Fore.LIGHTBLUE_EX + "Enter the source chat IDs (comma separated): " + Style.RESET_ALL).split(',')
        source_chat_ids = [int(chat_id.strip()) for chat_id in source_chat_ids]
        destination_channel_id = int(input(Fore.LIGHTBLUE_EX + "Enter the destination chat ID: " + Style.RESET_ALL))
        print(Fore.CYAN + "Enter keywords if you want to forward messages with specific keywords, or leave blank to forward every message!")
        keywords = input(Fore.LIGHTBLUE_EX + "Put keywords (comma separated if multiple, or leave blank): " + Style.RESET_ALL).split(',')
        
        await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords)
    else:
        print(Fore.RED + "Invalid choice")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())