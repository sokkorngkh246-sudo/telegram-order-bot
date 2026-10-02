import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
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
# ១. ការកំណត់ព័ត៌មានដើម (Configuration)
# ---------------------------------------------------------
BOT_TOKEN = "Your_token"    # ជំនួសដោយ Bot Token ដែលបានពី @BotFather
ADMIN_GROUP_ID = -185868658911         # ជំនួសដោយ Chat ID របស់ Admin Group (ឧ. -100xxxxxxxxxx)

# កំណត់ Stage សម្រាប់ការឆ្លើយឆ្លងជាជំហានៗ
CHOOSING_PRODUCT, GET_NAME, GET_PHONE, GET_ADDRESS = range(4)

# បញ្ជីទំនិញគំរូ (Catalog)
PRODUCTS = {
    "prod_1": {"name": "កាហ្វេទឹកដោះគោ (Iced Latte)", "price": 2.50},
    "prod_2": {"name": "តែបៃតង (Matcha Latte)", "price": 2.75},
    "prod_3": {"name": "កាហ្វេខ្មៅ (Americano)", "price": 2.00},
}

# Logging
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
    
    # បង្កើត Inline Buttons សម្រាប់បញ្ជីទំនិញ
    keyboard = [
        [InlineKeyboardButton(f"{p['name']} — ${p['price']:.2f}", callback_data=code)]
        for code, p in PRODUCTS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "សូមស្វាគមន៍មកកាន់ហាងរបស់យើង! ☕️🥤\n\nសូមជ្រើសរើសមុខទំនិញដែលអ្នកចង់កម្ម៉ង់៖",
        reply_markup=reply_markup
    )
    return CHOOSING_PRODUCT


async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកទំនិញដែលបានជ្រើសរើស រួចសួររកឈ្មោះ"""
    query = update.callback_query
    await query.answer()
    
    product_code = query.data
    selected_prod = PRODUCTS.get(product_code)
    
    if not selected_prod:
        await query.edit_message_text("មានបញ្ហាក្នុងការជ្រើសរើស។ សូមវាយ /start ឡើងវិញ។")
        return ConversationHandler.END

    # រក្សាទុកទំនិញក្នុង user_data
    context.user_data['order']['product'] = selected_prod['name']
    context.user_data['order']['price'] = selected_prod['price']
    
    await query.edit_message_text(
        f"អ្នកបានជ្រើសរើស៖ *{selected_prod['name']}* (${selected_prod['price']:.2f})\n\n"
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
    """ទទួលយកលេខទូរស័ព្ទ រួចសួររកអាសយដ្ឋាន"""
    phone = update.message.text
    context.user_data['order']['phone'] = phone
    
    await update.message.reply_text(
        "សូមបញ្ចូល *អាសយដ្ឋានដឹកជញ្ជូន* ឬផ្ញើទីតាំងរបស់អ្នក៖",
        parse_mode="Markdown"
    )
    return GET_ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ទទួលយកអាសយដ្ឋាន, បញ្ជក់ Order ជូនអ្នកទិញ និងផ្ញើ Notification ចូល Admin Group"""
    address = update.message.text
    order = context.user_data['order']
    order['address'] = address
    
    user = update.effective_user
    username_str = f"@{user.username}" if user.username else "គ្មាន Username"

    # ១. ផ្ញើសារបញ្ជាក់ជូនអ្នកកុម្ម៉ង់ (Customer)
    buyer_msg = (
        "✅ *ការកុម្ម៉ង់ត្រូវបានបញ្ជូនជោគជ័យ!*\n\n"
        f"☕️ *ទំនិញ:* {order['product']}\n"
        f"💵 *តម្លៃ:* ${order['price']:.2f}\n"
        f"👤 *ឈ្មោះ:* {order['name']}\n"
        f"📞 *លេខទូរស័ព្ទ:* {order['phone']}\n"
        f"📍 *អាសយដ្ឋាន:* {order['address']}\n\n"
        "ក្រុមការងារយើងខ្ញុំនឹងទាក់ទងទៅអ្នកក្នុងពេលឆាប់ៗនេះ។ អរគុណ!"
    )
    await update.message.reply_text(buyer_msg, parse_mode="Markdown")

    # ២. ផ្ញើសារជូនដំណឹងចូល Admin Group
    admin_msg = (
        "🔔 *មានការកុម្ម៉ង់ទំនិញថ្មី! (New Order)*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🛍 *មុខទំនិញ:* {order['product']}\n"
        f"💰 *តម្លៃ:* ${order['price']:.2f}\n"
        f"👤 *អតិថិជន:* {order['name']} ({username_str})\n"
        f"📞 *លេខទូរស័ព្ទ:* `{order['phone']}`\n"
        f"📍 *អាសយដ្ឋាន:* {order['address']}\n"
        f"🆔 *User ID:* `{user.id}`\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        await context.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=admin_msg,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"មិនអាចផ្ញើសារចូល Admin Group បានទេ៖ {e}")

    # បញ្ចប់ Conversation
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """បោះបង់ការកុម្ម៉ង់"""
    await update.message.reply_text(
        "ការកុម្ម៉ង់ត្រូវបានបោះបង់។ វាយ /start ដើម្បីចាប់ផ្តើមឡើងវិញ។",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# ---------------------------------------------------------
# ៣. មុខងារចម្បងសម្រាប់ដំណើរកា Bot (Main)
# ---------------------------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_PRODUCT: [CallbackQueryHandler(product_selected)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)

    print("🤖 Telegram Order Bot កំពុងដំណើរការ...")
    app.run_polling()

if __name__ == '__main__':
    main()