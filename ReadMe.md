# 🚀 Soluify Telegram Copy & Paste Bot

![Soluify Bot Logo](https://share.woahlab.com/-vXC6zguKx2)
[![Website](https://img.shields.io/website?label=soluify.com&style=plastic&url=https%3A%2F%2Fsoluify.com)](https://soluify.com/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=plastic&logo=linkedin)](https://www.linkedin.com/company/soluify)

Welcome to the **Soluify Telegram Copy & Paste Bot**! 🎉 This isn't just any bot—this is your new best friend in automating Telegram message management. Imagine having a super-efficient assistant that forwards messages between Telegram chats based on your specified keywords. Whether you're the mastermind behind multiple community groups, a diligent update tracker, or someone who just loves a bit of automation magic, this bot is here to make your life easier. Let's dive in!

---

## 🌟 Features

- **Optional Keyword-Based Forwarding:** Say goodbye to manual message forwarding! This bot automatically sends messages containing your chosen keywords to designated chats.
- **Multiple Source & Destination Chats:** Juggling multiple chats? No problem! Monitor and copy messages from various chats simultaneously with ease.
- **Custom Signatures:** Add a personal touch to your forwarded messages with customizable signatures.
- **Blacklisting:** Keep unwanted messages at bay by blocking any containing blacklisted words or characters.
- **User-Friendly:** No PhD in rocket science required here—set up is a breeze with minimal configuration needed.
- **Real-time Monitoring:** Stay on top of everything with continuous real-time message monitoring and forwarding.
- **It Just Works:** While other solutions might be clunky or confusing, this bot is straightforward and reliable.
- **& It Looks Nice:** Running this on a Linux will treat you to our beautiful color theme. Eye candy for the win! 🌈

---

## 🛠️ How it Works

The Soluify Bot harnesses the power of the [Telethon](https://github.com/LonamiWebs/Telethon) library to interact with the Telegram API. Once you set up the bot with your Telegram API credentials, you can list all your chats and pinpoint those you want to forward messages from. If you don't have your API credentials yet, you can grab them from your [Telegram account](https://my.telegram.org/apps).

1. **Authentication:** Provide your Telegram API ID, API hash, and phone number.
2. **Chat Selection:** List and select the chats you want to monitor for forwarding messages.
3. **Extra Configuration:** Specify keywords, add signatures, and more.

---

## 🔧 Getting Started

### Prerequisites

- **Python 3.7 or higher**
- Basic command line knowledge

### Installation Steps

Fire up your terminal and follow these steps:

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
    - **Add your API ID & Hash:** Get these from your [Telegram account](https://my.telegram.org/apps).
    - **Log into Telegram:** Enter your phone number (e.g., 447123456789) & approve with the 5-digit code Telegram sends you.

2. **Choose an option:**
    - **(1) List My Chat IDs:** View and select chats for message forwarding.
    - **(2) Configure Forwarding Messages:** Input the source chat ID, destination chat ID, and keywords to get the message forwarding party started.

---

## 📋 Notes

- **Common Sense:** Always read scripts you find online before running them to ensure your safety. Stay savvy!
- **Security:** Guard your API credentials like treasure and never share them publicly.
- **Permissions:** Make sure you have the necessary permissions to access messages in the chats you intend to use. You'll need read access to the source and write access to the destination.
- **Customization:** Feel free to tweak the script's behavior and settings to fit your unique needs.

---

## 📞 Contact

Got questions or need help? Don't hesitate to reach out to us [here](https://soluify.com/contact/). We're here for you!

---

## 🤝 Contributing

We love contributions! Here's how you can join the fun:

1. **Fork the repository** to your own GitHub account.
2. **Create a new branch** for your feature or bug fix.
3. **Make your changes** and commit them with clear messages.
4. **Submit a pull request** for review. Let's make this bot even better together!

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/license/mit). Check out the LICENSE link for more details.

---

Happy automating, and welcome to the future of Telegram message management! 🚀
