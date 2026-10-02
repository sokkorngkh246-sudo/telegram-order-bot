🛒 Telegram E-Commerce Order & Notification Bot

A lightweight, automated Telegram Order Management Bot built using Python. This bot simplifies the ordering process for local businesses and online merchants by collecting order details step-by-step from customers and instantly dispatching formatted order alerts to an Admin Group.

🌟 Key Features

Interactive Product Catalog: Displays dynamic product lists with prices using inline keyboard buttons.

Step-by-Step Order Flow: Built using ConversationHandler to guide users seamlessly through product selection, customer name, phone number, and delivery address.

Instant Admin Notifications: Automatically formats and routes incoming orders directly to a specified Telegram Admin Group for instant fulfillment.

User Confirmation: Provides a summary receipt to the buyer upon successful order placement.

Error Handling & Logging: Includes robust error catching and event logging for reliable operation.

🛠️ Tech Stack & Prerequisites

Language: Python 3.9+

Core Library: python-telegram-bot (v20.0+)

Deployment Friendly: Compatible with Render, Railway, PythonAnywhere, or Docker environments.

🚀 Getting Started

Follow these steps to set up and run the bot locally.

1. Prerequisites

Ensure you have Python installed on your machine:

python --version


2. Clone the Repository

git clone https://github.com/your-username/telegram-order-bot.git
cd telegram-order-bot


3. Install Dependencies

pip install -r requirements.txt


(Note: Create a requirements.txt file containing python-telegram-bot>=20.0)

⚙️ Configuration

Obtain Bot Token:

Open Telegram and search for @BotFather.

Create a new bot using /newbot and copy your HTTP API Token.

Obtain Admin Group Chat ID:

Create a Telegram Group and add your newly created bot to it.

Add @raw_data_bot to the group to obtain the Group Chat ID (e.g., -100xxxxxxxxx).

Update Script Credentials:
Open bot.py and replace the placeholder credentials with your own:

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_GROUP_ID = -100XXXXXXXXXX


💻 Running the Bot

Execute the main Python script:

python bot.py


📱 Bot Workflow / Preview

[ Customer ]                     [ Telegram Bot ]                  [ Admin Group ]
     |                                  |                                 |
     |---- 1. /start ------------------>|                                 |
     |<--- 2. Displays Product Menu ----|                                 |
     |---- 3. Selects Product --------->|                                 |
     |<--- 4. Asks Name/Phone/Address --|                                 |
     |---- 5. Inputs Details ----------->|                                 |
     |<--- 6. Sends Order Receipt ------|                                 |
     |                                  |---- 7. Sends Order Alert ------>|


🔮 Future Enhancements

[ ] Add ABA KHQR Automated Payment Gateway integration.

[ ] Connect SQLite/PostgreSQL database to store order history and inventory.

[ ] Add an Admin Web Dashboard to manage products and order status updates.

📜 License

Distributed under the MIT License. See LICENSE for more information.

🤝 Contact & Hiring

Developed with ❤️ by [/Your GitHub Profile]

Telegram: [@YourTelegramHandle]

Email: your.email@example.com

LinkedIn: linkedin.com/in/yourprofile

