import os
import logging
from threading import Thread
from flask import Flask

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ---------------------------------------------------------
# ០. បង្កើត Web Server ការពារ Port Timeout លើ Render Web Service
# ---------------------------------------------------------
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ---------------------------------------------------------
# ១. ការកំណត់ព័ត៌មានដើម (Configuration)
# ---------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID_ENV = os.getenv("ADMIN_GROUP_ID", "-185868658911")

try:
    ADMIN_GROUP_ID = int(ADMIN_GROUP_ID_ENV)
except ValueError:
    ADMIN_GROUP_ID = -185868658911

# កំណត់ Stage សម្រាប់ការឆ្លើយឆ្លងជាជំហានៗ
(
    CHOOSING_PRODUCT,
    CHOOSING_QTY,
    CHOOSING_SUGAR,
    GET_NAME,
    GET_PHONE,
    GET_LOCATION_OR_ADDRESS,
    PAYMENT_SLIP,
) = range(7)

# បញ្ជីទំនិញ (Catalog)
PRODUCTS = {
    # កាហ្វេ
    "prod_1": {"name": "កាហ្វេទឹកដោះគោ (Iced Latte)", "price": 2.50, "has_sugar": True},
    "prod_2": {"name": "កាហ្វេខ្មៅ (Americano)", "price": 2.00, "has_sugar": True},
    "prod_3": {"name": "កាហ្វេកាពូឈីណូ (Cappuccino)", "price": 2.75, "has_sugar": True},
    "prod_4": {"name": "កាហ្វេម៉ូកា (Iced Mocha)", "price": 3.00, "has_sugar": True},
    # តែ & ភេសជ្ជៈ
    "prod_5": {"name": "តែបៃតង (Matcha Latte)", "price": 2.75, "has_sugar": True},
    "prod_6": {"name": "តែក្រូចឆ្មារ (Iced Lemon Tea)", "price": 2.00, "has_sugar": True},
    "prod_7": {"name": "តែថៃ (Thai Milk Tea)", "price": 2.25, "has_sugar": True},
    "prod_8": {"name": "ឆូកូឡាត (Chocolate)", "price": 2.75, "has_sugar": True},
    # នំ & បង្អែម
    "prod_9": {"name": "នំប្រូសង់ (Croissant)", "price": 1.75, "has_sugar": False},
    "prod_10": {"name": "នំខេកឆូកូឡាត (Chocolate Cake)", "price": 3.25, "has_sugar": False},
}

# Logging (កែប្រែ Syntax ត្រឹមត្រូវ)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------
# ២. Functions គ្រប់គ្រង Flow នៃការកុម្ម៉ង់ (Conversation Handlers)
# ---------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ចាប់ផ្តើម Bot និងបង្ហាញបញ្ជីទំនិញ"""
    context.user_data['order'] = {}
    
    keyboard = [
        [InlineKeyboardButton(f"{p['name']} — ${p['price']:.2f}", callback_data=code)]
        for code, p in PRODUCTS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "សូមស្វាគមន៍មកកាន់ហាងរបស់យើង! ☕️🥤\n\nសូមជ្រើសរើសមុខទំនិញដែលអ្នកចង់កុម្ម៉ង់៖",
        reply_markup=reply_markup
    )
    return CHOOSING_PRODUCT


async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកទំនិញ រួចសួររកចំនួន (Quantity)"""
    query = update.callback_query
    await query.answer()
    
    product_code = query.data
    selected_prod = PRODUCTS.get(product_code)
    
    if not selected_prod:
        await query.edit_message_text("មានបញ្ហាក្នុងការជ្រើសរើស។ សូមវាយ /start ឡើងវិញ។")
        return ConversationHandler.END

    context.user_data['order']['product_code'] = product_code
    context.user_data['order']['product'] = selected_prod['name']
    context.user_data['order']['unit_price'] = selected_prod['price']
    context.user_data['order']['has_sugar'] = selected_prod['has_sugar']
    
    # ប៊ូតុងជ្រើសរើសចំនួន 1 ដល់ 6
    qty_keyboard = [
        [
            InlineKeyboardButton("1", callback_data="qty_1"),
            InlineKeyboardButton("2", callback_data="qty_2"),
            InlineKeyboardButton("3", callback_data="qty_3"),
        ],
        [
            InlineKeyboardButton("4", callback_data="qty_4"),
            InlineKeyboardButton("5", callback_data="qty_5"),
            InlineKeyboardButton("6", callback_data="qty_6"),
        ]
    ]
    
    msg_text = (
        f"អ្នកបានជ្រើសរើស៖ *{selected_prod['name']}* (${selected_prod['price']:.2f})\n\n"
        "សូមជ្រើសរើស *ចំនួន (Quantity)* ៖"
    )
    
    await query.edit_message_text(
        msg_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(qty_keyboard)
    )
    return CHOOSING_QTY


async def qty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកចំនួន រួចសួររកកម្រិតស្ករ (ប្រសិនបើជាភេសជ្ជៈ)"""
    query = update.callback_query
    await query.answer()
    
    qty = int(query.data.split('_')[1])
    unit_price = context.user_data['order']['unit_price']
    
    context.user_data['order']['qty'] = qty
    context.user_data['order']['total_price'] = qty * unit_price

    # ប្រសិនបើជាទំនិញប្រភេទភេសជ្ជៈ សួររកកម្រិតស្ករ
    if context.user_data['order']['has_sugar']:
        sugar_keyboard = [
            [
                InlineKeyboardButton("100% (ផ្អែមធម្មតា)", callback_data="sugar_100%"),
                InlineKeyboardButton("75% (ផ្អែមល្មម)", callback_data="sugar_75%"),
            ],
            [
                InlineKeyboardButton("50% (ផ្អែមតិច)", callback_data="sugar_50%"),
                InlineKeyboardButton("25% (ផ្អែមតិចបំផុត)", callback_data="sugar_25%"),
            ],
            [
                InlineKeyboardButton("0% (គ្មានស្ករ)", callback_data="sugar_0%"),
            ]
        ]
        
        msg_text = (
            f"ចំនួន៖ *{qty}* (សរុប៖ *${context.user_data['order']['total_price']:.2f}*)\n\n"
            "សូមជ្រើសរើស *កម្រិតស្ករ (Sugar Level)* ៖"
        )
        await query.edit_message_text(
            msg_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(sugar_keyboard)
        )
        return CHOOSING_SUGAR
    else:
        context.user_data['order']['sugar'] = "N/A"
        msg_text = (
            f"ចំនួន៖ *{qty}* (សរុប៖ *${context.user_data['order']['total_price']:.2f}*)\n\n"
            "សូមបញ្ចូល *ឈ្មោះ* របស់អ្នកសម្រាប់ទាក់ទង៖"
        )
        await query.edit_message_text(
            msg_text,
            parse_mode="Markdown"
        )
        return GET_NAME


async def sugar_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកកម្រិតស្ករ រួចសួររកឈ្មោះ"""
    query = update.callback_query
    await query.answer()
    
    sugar_level = query.data.split('_')[1]
    context.user_data['order']['sugar'] = sugar_level
    
    await query.edit_message_text(
        f"កម្រិតស្ករ៖ *{sugar_level}*\n\n"
        "សូមបញ្ចូល *ឈ្មោះ* របស់អ្នកសម្រាប់ទាក់ទង៖",
        parse_mode="Markdown"
    )
    return GET_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកឈ្មោះ រួចសួររកលេខទូរស័ព្ទ"""
    user_name = update.message.text
    context.user_data['order']['name'] = user_name
    
    await update.message.reply_text(
        f"អរគុណ {user_name}!\n\nសូមបញ្ចូល *លេខទូរស័ព្ទ* របស់អ្នក៖",
        parse_mode="Markdown"
    )
    return GET_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកលេខទូរស័ព្ទ រួចសួររកអាសយដ្ឋាន/ទីតាំង GPS"""
    phone = update.message.text
    context.user_data['order']['phone'] = phone
    
    location_keyboard = [
        [KeyboardButton("📍 ផ្ញើទីតាំងបច្ចុប្បន្ន (Send Location)", request_location=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(location_keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "សូមចុចប៊ូតុងខាងក្រោមដើម្បី *ផ្ញើទីតាំងបច្ចុប្បន្ន (GPS)* ឬវាយបញ្ចូល *អាសយដ្ឋាន* ជាអក្សរ៖",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    return GET_LOCATION_OR_ADDRESS


async def get_location_or_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកទីតាំង GPS ឬអាសយដ្ឋានអក្សរ រួចបង្ហាញព័ត៌មានទូទាត់ប្រាក់"""
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        context.user_data['order']['address'] = f"https://maps.google.com/?q={lat},{lon}"
        context.user_data['order']['is_location'] = True
    else:
        context.user_data['order']['address'] = update.message.text
        context.user_data['order']['is_location'] = False

    order = context.user_data['order']
    
    pay_msg = (
        f"💵 *តម្លៃសរុបត្រូវទូទាត់៖ ${order['total_price']:.2f}*\n\n"
        "💳 *ព័ត៌មានគណនីទូទាត់ (ABA / KHQR)៖*\n"
        "• ឈ្មោះគណនី៖ *COFFEE SHOP DEMO*\n"
        "• លេខគណនី ABA៖ `000 123 456`\n\n"
        "📸 សូមផ្ញើរូបថត *Slip / វិក្កយបត្រ* ទូទាត់ប្រាក់ដើម្បីបញ្ចប់ការកុម្ម៉ង់៖"
    )
    
    await update.message.reply_text(
        pay_msg,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return PAYMENT_SLIP


async def payment_slip_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយក Slip រួចផ្ញើជូនដំណឹងចូល Admin Group"""
    photo_file_id = update.message.photo[-1].file_id
    order = context.user_data['order']
    user = update.effective_user
    username_str = f"@{user.username}" if user.username else "គ្មាន Username"

    sugar_info = f"\n🍬 *កម្រិតស្ករ:* {order['sugar']}" if order['has_sugar'] else ""
    loc_info = f"[ចុចមើលទីតាំងលើ Google Maps]({order['address']})" if order.get('is_location') else order['address']

    # ១. សារបញ្ជាក់ជូនអតិថិជន
    buyer_msg = (
        "✅ *ទទួលបានការកុម្ម៉ង់ និង Slip ទូទាត់រួចរាល់!*\n\n"
        f"☕️ *ទំនិញ:* {order['product']}\n"
        f"🔢 *ចំនួន:* {order['qty']}{sugar_info}\n"
        f"💵 *តម្លៃសរុប:* ${order['total_price']:.2f}\n"
        f"👤 *ឈ្មោះ:* {order['name']}\n"
        f"📞 *លេខទូរស័ព្ទ:* {order['phone']}\n\n"
        "ក្រុមការងារយើងខ្ញុំនឹងរៀបចំជូនក្នុងពេលឆាប់ៗនេះ។ អរគុណ!"
    )
    await update.message.reply_text(buyer_msg, parse_mode="Markdown")

    # ២. ផ្ញើសារ + រូបភាព Slip ចូល Admin Group
    admin_msg = (
        "🔔 *មានការកុម្ម៉ង់ទំនិញថ្មី! (New Paid Order)*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🛍 *មុខទំនិញ:* {order['product']}\n"
        f"🔢 *ចំនួន:* {order['qty']}{sugar_info}\n"
        f"💰 *តម្លៃសរុប:* ${order['total_price']:.2f}\n"
        f"👤 *អតិថិជន:* {order['name']} ({username_str})\n"
        f"📞 *លេខទូរស័ព្ទ:* `{order['phone']}`\n"
        f"📍 *អាសយដ្ឋាន/ទីតាំង:* {loc_info}\n"
        f"🆔 *User ID:* `{user.id}`\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        await context.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=photo_file_id,
            caption=admin_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"មិនអាចផ្ញើសារចូល Admin Group បានទេ៖ {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """បោះបង់ការកុម្ម៉ង់"""
    await update.message.reply_text(
        "ការកុម្ម៉ង់ត្រូវបានបោះបង់។ វាយ /start ដើម្បីចាប់ផ្តើមឡើងវិញ។",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ---------------------------------------------------------
# ៣. មុខងារចម្បង (Main)
# ---------------------------------------------------------
def main():
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN មិនទាន់ត្រូវបានកំណត់ក្នុង Environment Variables ទេ!")
        return

    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_PRODUCT: [CallbackQueryHandler(product_selected)],
            CHOOSING_QTY: [CallbackQueryHandler(qty_selected)],
            CHOOSING_SUGAR: [CallbackQueryHandler(sugar_selected)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_LOCATION_OR_ADDRESS: [
                MessageHandler(filters.LOCATION | (filters.TEXT & ~filters.COMMAND), get_location_or_address)
            ],
            PAYMENT_SLIP: [MessageHandler(filters.PHOTO, payment_slip_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)

    print("🤖 Telegram Order Bot កំពុងដំណើរការ...")
    app.run_polling()

if __name__ == '__main__':
    main()