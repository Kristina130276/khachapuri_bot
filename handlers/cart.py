from telegram import Update
from telegram.ext import ContextTypes
from data.menu import menu_data
from data.translations import translations
from handlers.order import ask_phone
from utils.order_summary import format_order_summary
import os

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "lang_en")
    cart = context.user_data.setdefault("cart", {})
    item_name = query.data.replace("add_", "")

    menu_items = menu_data.get(lang, [])
    price = next((item["price"] for item in menu_items if item["name"] == item_name), 0)

    if item_name in cart:
        cart[item_name]["qty"] += 1
    else:
        cart[item_name] = {"qty": 1, "price": price}

    await query.message.reply_text(
        translations[lang]["added_to_cart"].format(item=item_name, qty=cart[item_name]["qty"])
    )

async def done_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "lang_en")
    cart = context.user_data.get("cart", {})

    if not cart:
        await query.message.reply_text(translations[lang]["cart_empty"])
        return

    total = 0
    lines = []

    for item_name, data in cart.items():
        qty = data["qty"]
        price = data["price"]
        line_total = qty * price
        total += line_total
        lines.append(f"{item_name} × {qty} = {line_total}₪")

    summary = translations[lang]["order_summary"].format(
        items="\n".join(lines),
        total=total
    )

    await query.message.reply_text(summary)

    # Сохраняем total в context.user_data для итогового сообщения
    context.user_data["total_price"] = total

    # Переход к следующему шагу — сбор номера телефона
    await ask_phone(update, context)

    # Отправка админу предварительного заказа
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=format_order_summary(context.user_data)
    )
