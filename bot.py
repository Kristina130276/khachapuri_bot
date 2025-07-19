from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from handlers.start import start, set_language
from handlers.menu import show_menu
from handlers.cart import add_to_cart, done_order
from handlers.order import (
    handle_contact,
    handle_address,
    ask_phone,
    handle_delivery_option,
    handle_time_selected
)

import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Start
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))

# Menu and cart
app.add_handler(CallbackQueryHandler(show_menu, pattern="^menu$"))
app.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_"))
app.add_handler(CallbackQueryHandler(done_order, pattern="^done_order$"))

# Contact and address
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))

# Delivery options and time
app.add_handler(CallbackQueryHandler(handle_delivery_option, pattern="^delivery_"))
app.add_handler(CallbackQueryHandler(handle_time_selected, pattern="^time_"))

print("Bot is running...")
app.run_polling()
