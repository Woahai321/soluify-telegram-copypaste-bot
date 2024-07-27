# Soluify Telegram Copy & Paste Bot (Python Script)

The **Soluify Telegram Copy & Paste Bot** is a versatile Python script designed to automate the forwarding of messages between Telegram chats (groups or channels) based on specified keywords. Whether you're a developer or a general user, this tool makes it easy to keep track of important messages without manual intervention.

---

## 🌟 Features

- **Keyword-Based Forwarding:** Automatically forward messages containing specific keywords from one chat to another.
- **User-Friendly:** Easy to set up with minimal configuration required.
- **Real-time Monitoring:** Continuously monitors and forwards messages in real-time.

---

## 🛠️ How it Works

The script leverages the [Telethon](https://github.com/LonamiWebs/Telethon) library to interact with the Telegram API. After providing your Telegram API ID, API hash, and phone number for authentication, you can list all your chats and select those for message forwarding. The script then monitors the specified source chat and forwards messages containing any of the specified keywords to the destination chat.

---

## 🔑 Keywords

Specify one or more keywords that, if found in a message, will trigger the forwarding process. Keywords are case-insensitive and can be set up during the initial configuration.

---

## 🚀 Setup and Usage

1. **Clone the repository:**

    ```
    git clone https://github.com/{fill-in}
    cd Soluify-Telegram-Copy-Paste-Bot
    ```

2. **Install the required dependencies:**

    ```
    pip install -r requirements.txt
    ```

3. **Configure the script:**

    - Open the `SoluifyCopier.py` file and input your Telegram API ID, API hash, and phone number in the designated variables.
    - Adjust other settings as necessary directly within the script.

4. **Run the script:**

    ```
    python SoluifyCopier.py
    ```

5. **Choose an option:**
    - **(1) List Chats:** View and select chats to use for message forwarding.
    - **(2) Forward Messages:** Input the source chat ID, destination chat ID, and keywords to initiate message forwarding.

---

## 📋 Notes

- **Common Sense:** Always read scripts you find online before running them to ensure your safety.
- **Security:** Keep your API credentials secure and never share them publicly.
- **Permissions:** Ensure you have the necessary permissions to access messages in the chats you intend to use. You will require read access to source and write to destination.
- **Customization:** Feel free to adjust the script's behavior and settings according to your specific requirements.

---

## 📞 Contact

For any queries or issues, please reach out to us [here](https://soluify.com/contact/).

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://rem.mit-license.org) file for more details.
