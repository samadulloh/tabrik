import logging
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from image_generator import generate_card, get_themes

BOT_TOKEN = "8681433587:AAHK4K7e61IshM50hmsLnATGkNOs7A46BSI"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_sessions = {}
subscribed_users = set()

HOLIDAYS = {
    "ramazon_2026": {"date": "2026-03-20", "type": "ramazon"},
    "qurbon_2026":  {"date": "2026-05-27", "type": "qurbon"},
    "arafa_2026":   {"date": "2026-05-26", "type": "arafa"},
}

FAMILY_MEMBERS = [
    ("👴", "Bobojonim"),
    ("👵", "Buvijonim"),
    ("👨", "Dadajonim"),
    ("👩", "Onajonim"),
    ("👩", "Opajonim"),
    ("👧", "Singiljonim"),
    ("👦", "Akajonim"),
    ("👦", "Ukajonim"),
    ("👶", "Jiyanjonim"),
    ("👩‍🦱", "Xolajonim"),
    ("👩‍🦱", "Ammajonim"),
    ("🧔‍♂️", "Tog'ajonim"),
    ("🧔‍♂️", "Amakijonim"),

]

def main_reply_keyboard():
    keyboard = [
        [KeyboardButton("👥 Do'stlarni tabriklash"), KeyboardButton("👨‍👩‍👧‍👦 Oilani tabriklash")],
        [KeyboardButton("📅 Keyingi bayram")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def holiday_keyboard(prefix="holiday"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌙 Ramazon Hayiti", callback_data=f"{prefix}_ramazon")],
        [InlineKeyboardButton("🐑 Qurbon Hayiti", callback_data=f"{prefix}_qurbon")],
        [InlineKeyboardButton("🤲 Arafa kuni", callback_data=f"{prefix}_arafa")],
    ])

def family_keyboard():
    keyboard = []
    row = []
    for emoji, name in FAMILY_MEMBERS:
        row.append(InlineKeyboardButton(f"{emoji} {name}", callback_data=f"family_{name}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def send_all_cards(context, chat_id, name, holiday):
    holiday_emoji = {"ramazon": "🌙", "qurbon": "🐑", "arafa": "🤲"}.get(holiday, "🎉")
    holiday_name = {"ramazon": "Ramazon Hayiti", "qurbon": "Qurbon Hayiti", "arafa": "Arafa kuni"}.get(holiday, "Hayit")

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"{holiday_emoji} *{name}*ga {holiday_name} tabrigi yaratilmoqda...",
        parse_mode='Markdown'
    )

    themes = get_themes(holiday)
    for i in range(len(themes)):
        try:
            image_path = generate_card(name, holiday, i)
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                )
            os.remove(image_path)
        except Exception as e:
            logger.error(f"Rasm {i} yaratishda xato: {e}")

    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ Hammasi tayyor! Yaqinlaringizga yuboring 💌",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Yana tabrik yaratish", callback_data="back_start")]
        ])
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    subscribed_users.add(user.id)
    user_sessions.pop(user.id, None)
    text = (
        f"✨ *Assalomu alaykum, {user.first_name}!*\n\n"
        "Men siz uchun do'stlaringiz va oila a'zolaringizni "
        "*Ramazon*, *Arafa* va *Qurbon Hayiti* bilan "
        "tabriklovchi *chiroyli kartochkalar* yarataman! 🎨\n\n"
        "👇 Quyidagi tugmani bosing:"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_reply_keyboard())
    else:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(text, parse_mode='Markdown', reply_markup=main_reply_keyboard())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if text == "👥 Do'stlarni tabriklash":
        user_sessions[user_id] = {"step": "holiday", "type": "friend"}
        await update.message.reply_text(
            "🎉 *Qaysi bayram uchun tabrik?*",
            parse_mode='Markdown',
            reply_markup=holiday_keyboard("holiday")
        )
        return

    if text == "👨‍👩‍👧‍👦 Oilani tabriklash":
        user_sessions[user_id] = {"step": "holiday", "type": "family"}
        await update.message.reply_text(
            "👨‍👩‍👧‍👦 *Qaysi bayram uchun?*",
            parse_mode='Markdown',
            reply_markup=holiday_keyboard("fholiday")
        )
        return

    if text == "📅 Keyingi bayram":
        today = datetime.now().date()
        upcoming = []
        names = {"ramazon": "🌙 Ramazon Hayiti", "qurbon": "🐑 Qurbon Hayiti", "arafa": "🤲 Arafa kuni"}
        for key, h in HOLIDAYS.items():
            d = datetime.strptime(h["date"], "%Y-%m-%d").date()
            if d >= today:
                days = (d - today).days
                upcoming.append((days, names[h["type"]], h["date"]))
        upcoming.sort()
        if upcoming:
            days, name, date = upcoming[0]
            msg = f"🎉 Bugun *{name}*!\nHayitingiz muborak! 🎊" if days == 0 else f"📅 Keyingi bayram:\n\n*{name}*\n🗓 {date}\n⏳ *{days} kun* qoldi"
        else:
            msg = "Hozircha ma'lumot yo'q."
        await update.message.reply_text(msg, parse_mode='Markdown')
        return

    session = user_sessions.get(user_id, {})
    if session.get("step") == "name":
        name = text
        if len(name) > 30:
            await update.message.reply_text("❌ Ism juda uzun! Iltimos, qisqaroq yozing.")
            return
        holiday = session.get("holiday", "qurbon")
        user_sessions[user_id]["step"] = "done"
        await send_all_cards(context, update.message.chat_id, name, holiday)

async def holiday_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    holiday = query.data.split("_")[1]
    user_sessions[query.from_user.id] = {"step": "name", "holiday": holiday}
    await query.message.reply_text(
        "✍️ *Do'stingizning ismini yozing:*\n_Masalan: Ali, Malika..._",
        parse_mode='Markdown'
    )

async def family_holiday_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    holiday = query.data.split("_")[1]
    user_sessions[query.from_user.id] = {"step": "family_member", "holiday": holiday}
    await query.message.reply_text(
        "👨‍👩‍👧‍👦 *Kimni tabriklaymiz?*",
        parse_mode='Markdown',
        reply_markup=family_keyboard()
    )

async def family_member_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    name = query.data.replace("family_", "")
    user_id = query.from_user.id
    holiday = user_sessions.get(user_id, {}).get("holiday", "qurbon")
    user_sessions[user_id] = {"step": "done"}
    await send_all_cards(context, query.message.chat_id, name, holiday)

async def send_holiday_greetings(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    for key, holiday in HOLIDAYS.items():
        if holiday["date"] == today:
            for user_id in subscribed_users:
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="🎉 Bugun bayram! /start bosib tabrik kartochkasi yarating!"
                    )
                except Exception as e:
                    logger.error(f"Xato: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(holiday_chosen, pattern="^holiday_"))
    app.add_handler(CallbackQueryHandler(family_holiday_chosen, pattern="^fholiday_"))
    app.add_handler(CallbackQueryHandler(family_member_chosen, pattern="^family_"))
    app.add_handler(CallbackQueryHandler(start, pattern="^back_start$"))

    app.job_queue.run_daily(
        send_holiday_greetings,
        time=datetime.strptime("08:00", "%H:%M").time()
    )

    logger.info("Bot ishga tushdi! ✅")
    app.run_polling()

if __name__ == '__main__':
    main()