def format_order_summary(user_data: dict) -> str:
    cart = user_data.get("cart", {})
    address = user_data.get("address", "—")
    phone = user_data.get("phone", "—")
    delivery_time = user_data.get("delivery_time", "—")

    lines = []
    total = 0

    for item, data in cart.items():
        qty = data["qty"]
        price = data["price"]
        subtotal = qty * price
        lines.append(f"{item} × {qty} = {subtotal} ₪")
        total += subtotal

    order_text = "\n".join(lines)

    summary = (
        f"🧾 *New Order Received!*\n\n"
        f"{order_text}\n"
        f"💰 Total: {total} ₪\n\n"
        f"📞 Phone: {phone}\n"
        f"📍 Address: {address}\n"
        f"🕒 Delivery time: {delivery_time}"
    )

    return summary
