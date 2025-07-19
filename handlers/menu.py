from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data.menu import menu_data
from data.translations import translations

async def show_menu(update, context):
    lang = context.user_data.get("lang", "lang_en")
    if lang not in translations:
        lang = "lang_en"

    t = translations.get(lang, {})
    choose_from_menu_text = t.get("choose_from_menu", "Please choose from the menu:")
    done_order_btn_text = t.get("done_order_btn", "✅ Done ordering")

    menu_items = menu_data.get(lang, [])
    chat_id = update.effective_chat.id

    # Отправляем каждое блюдо как фото с кнопкой
    for item in menu_items:
        name = item.get("name", "Item")
        price = item.get("price", "?")
        photo_url = item.get("image")  # предполагается, что в menu_data есть ключ "image"

        caption = f"{name} - {price}₪"
        button = InlineKeyboardButton(text=f"{caption}", callback_data=f"add_{name}")
        reply_markup = InlineKeyboardMarkup([[button]])

        if photo_url:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=caption,
                reply_markup=reply_markup
            )

    # Кнопка завершения заказа
    done_button = InlineKeyboardMarkup([[
        InlineKeyboardButton(text=done_order_btn_text, callback_data="done_order")
    ]])

    await context.bot.send_message(
        chat_id=chat_id,
        text=choose_from_menu_text,
        reply_markup=done_button
    )
