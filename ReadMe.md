# Soluify Telegram Copy & Paste Bot (Python Script)

The **Soluify Telegram Copy & Paste Bot** is a versatile Python script designed to automate the forwarding of messages between Telegram chats (groups or channels) based on specified keywords. Whether you're a developer or a general user, this tool makes it easy to keep track of important messages without manual intervention.

---

## 🌟 Features

- **Keyword-Based Forwarding:** Automatically forward messages containing specific keywords between chats.
- **Multiple Source Chats:** Copy from more than one source location.
- **Signature:** Add a signature that appends to the end of every message forwarded.
- **User-Friendly:** Easy to set up with minimal configuration required.
- **Real-time Monitoring:** Continuously monitors and forwards messages in real-time.

---

## 🛠️ How it Works

The script leverages the [Telethon](https://github.com/LonamiWebs/Telethon) library to interact with the Telegram API. After providing your Telegram API ID, API hash, and phone number for authentication, you can list all your chats and select those for message forwarding. You can obtain your API details from you [telegram account](https://my.telegram.org/apps). The script then monitors the specified source chat and forwards messages containing any of the specified keywords to the destination chat.

---

## 🔑 Keywords

Specify one or more keywords that, if found in a message, will trigger the forwarding process. Keywords are case-insensitive and can be set up during the initial configuration.

---

## ✍️ Signatures

Add a signature in bold to the end of every message that gets forwarded by the script.

---

## 🚀 Setup and Usage

1. **Clone the repository:**

    ```
    git clone https://github.com/Woahai321/soluify-telegram-copypaste-bot.git
    cd soluify-telegram-copypaste-bot
    ```

2. **Install the required dependencies:**

    ```
    pip install -r requirements.txt
    ```

3. **Run the script:**

    ```
    python SoluifyCopier.py
    ```

4. **Fill in the required details when prompted:**
    - **Add your API ID & Hash:** These can be obtained from you [telegram account](https://my.telegram.org/apps).
    - **Log into Telegram:** Input your phone number (e.g., 447123456789) & approve with the 5 digit code provided by Telegram.

5. **Choose an option:**
    - **(1) List My Chat IDs:** View and select chats to use for message forwarding.
    - **(2) Configure Forwarding Messages:** Input the source chat ID, destination chat ID, and keywords to initiate message forwarding.

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

This project is licensed under the MIT License. See [LICENSE](https://opensource.org/license/mit) for more details.
