# 🚀 Soluify Telegram Copy & Paste Bot

![Soluify Bot Logo](https://share.woahlab.com/-Xsc9BSF47n)

**Soluify Telegram Copy & Paste Bot** is a powerful automation tool designed to streamline your Telegram message management. This Python script allows users to effortlessly forward messages between Telegram chats based on specific keywords. Whether you're managing community groups, tracking important updates, or simply want to automate message forwarding, this bot is your ideal solution!

---

## 🌟 Features

- **Keyword-Based Forwarding:** Automatically forward messages containing specified keywords to designated chats.
- **Multiple Source Chats:** Monitor and copy messages from various chats simultaneously.
- **Custom Signatures:** Personalize forwarded messages with customizable signatures.
- **User-Friendly:** Easy to set up with minimal configuration required.
- **Real-time Monitoring:** Continuously monitors and forwards messages in real-time.

---

## 🛠️ How it Works

The Soluify Bot leverages the [Telethon](https://github.com/LonamiWebs/Telethon) library to interact with the Telegram API. After setting up the bot with your Telegram API credentials, you can list all your chats and identify those for message forwarding. You can obtain your API credentials from your [Telegram account](https://my.telegram.org/apps).

1. **Authentication:** Provide your Telegram API ID, API hash, and phone number.
2. **Chat Selection:** List and select chats for forwarding messages.
3. **Keyword Setup:** Specify keywords that will trigger the forwarding action.

---

## 🔧 Getting Started

### Prerequisites

- **Python 3.7 or higher**
- Basic command line knowledge

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/Woahai321/soluify-telegram-copypaste-bot.git
cd soluify-telegram-copypaste-bot

# Install dependencies
pip install -r requirements.txt

# Run the script
python SoluifyCopier.py
```

### Configuration

1. **Fill in the required details when prompted:**
    - **Add your API ID & Hash:** These can be obtained from your [Telegram account](https://my.telegram.org/apps).
    - **Log into Telegram:** Input your phone number (e.g., 447123456789) & approve with the 5 digit code provided by Telegram.

2. **Choose an option:**
    - **(1) List My Chat IDs:** View and select chats to use for message forwarding.
    - **(2) Configure Forwarding Messages:** Input the source chat ID, destination chat ID, and keywords to initiate message forwarding.
---

## 📋 Notes

- **Common Sense:** Don't rush! Always read scripts you find online before running them to ensure your own safety. 
- **Security:** Keep your API credentials secure and never share them publicly.
- **Permissions:** Ensure you have the necessary permissions to access messages in the chats you intend to use. You will require read access to source and write to destination.
- **Customization:** Feel free to adjust the script's behavior and settings according to your specific requirements.

---

## 📞 Contact

For any queries or issues, please reach out to us [here](https://soluify.com/contact/).

---

## 🤝 Contributing

We welcome contributions! Here’s how you can help:

1. **Fork the repository** to your own GitHub account.
2. **Create a new branch** for your feature or bug fix.
3. **Make your changes** and commit them with clear messages.
4. **Submit a pull request** for review.

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/license/mit). See the LICENSE file for more details.

---