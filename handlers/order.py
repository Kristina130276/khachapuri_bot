# handlers/order.py

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import ContextTypes
from data.translations import translations
from utils.order_summary import format_order_summary
import os

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "lang_en")
    button = KeyboardButton("📞 Share phone number", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)

    message_text = translations.get(lang, translations["lang_en"]).get(
        "next_step_phone", "📞 Please share your phone number:"
    )

    if update.message:
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(message_text, reply_markup=reply_markup)


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        contact = update.message.contact
        context.user_data["phone"] = contact.phone_number

        await update.message.reply_text(f"📱 {contact.phone_number} ✅")

        lang = context.user_data.get("lang", "lang_en")
        prompt = translations.get(lang, translations["lang_en"]).get(
            "next_step_address", "🏠 Please enter your delivery address:"
        )
        await update.message.reply_text(prompt)

    except Exception as e:
        print("❌ Error in handle_contact:", e)
        await update.message.reply_text("⚠️ Something went wrong with phone number.")


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        lang = context.user_data.get("lang", "lang_en")
        address = update.message.text
        context.user_data["address"] = address

        await update.message.reply_text(f"📍 {address} ✅")
        await ask_delivery_options(update, context)

    except Exception as e:
        print("❌ Error in handle_address:", e)
        await update.message.reply_text("⚠️ Something went wrong while processing your address.")


async def ask_delivery_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "lang_en")

    asap_text = translations.get(lang, translations["lang_en"]).get(
        "delivery_asap", "🚀 Deliver ASAP"
    )
    select_time_text = translations.get(lang, translations["lang_en"]).get(
        "delivery_select_time", "⏰ Select delivery time"
    )
    prompt = translations.get(lang, translations["lang_en"]).get(
        "choose_delivery_option", "🚚 Choose a delivery option:"
    )

    buttons = [
        [InlineKeyboardButton(asap_text, callback_data="delivery_asap")],
        [InlineKeyboardButton(select_time_text, callback_data="delivery_custom")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(prompt, reply_markup=reply_markup)


async def handle_delivery_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "lang_en")

    if query.data == "delivery_asap":
        context.user_data["delivery_time"] = "ASAP"
        await finish_order(query, context)

    elif query.data == "delivery_custom":
        await ask_time_slots(query, context)


async def ask_time_slots(query, context):
    lang = context.user_data.get("lang", "lang_en")
    prompt = translations.get(lang, translations["lang_en"]).get(
        "choose_time", "⏰ Choose delivery time:"
    )
    hours = range(10, 23)

    buttons = [
        [InlineKeyboardButton(f"{hour}:00", callback_data=f"time_{hour}:00")] for hour in hours
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(prompt, reply_markup=reply_markup)


async def handle_time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    time_selected = query.data.replace("time_", "")
    context.user_data["delivery_time"] = time_selected

    await finish_order(query, context)


async def finish_order(query, context):
    lang = context.user_data.get("lang", "lang_en")
    summary = format_order_summary(context.user_data)

    confirmation = translations.get(lang, translations["lang_en"]).get(
        "order_sent", "🧾 Order sent successfully!"
    )

    await query.edit_message_text(confirmation)

    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
        except Exception as e:
            print("❌ Failed to send order to admin:", e)
    context.user_data["cart"] = {}
    context.user_data["phone"] = None
    context.user_data["address"] = None
    context.user_data["delivery_time"] = None

