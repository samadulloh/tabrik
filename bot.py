import logging
import os
import asyncio
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from image_generator import generate_card, get_themes
from database import (
    init_db, close_pool,
    save_user, get_all_active_users, deactivate_user,
    save_request,
    get_cached_file_id, save_cache,
    get_stats,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_sessions = {}

HOLIDAYS = {
    "ramazon_2026": {"date": "2026-03-20", "type": "ramazon"},
    "qurbon_2026":  {"date": "2026-05-27", "type": "qurbon"},
    "arafa_2026":   {"date": "2026-05-26", "type": "arafa"},
}

ADMIN_IDS = {6389229653}  # Admin user_id larini shu yerga qo'shing: {123456789, 987654321}


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



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id, user.first_name, user.username)
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


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Faqat adminlar uchun /stats komandasi"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Ruxsat yo'q.")
        return

    data = await get_stats()
    holiday_names = {"ramazon": "🌙 Ramazon", "qurbon": "🐑 Qurbon", "arafa": "🤲 Arafa"}

    popular = "\n".join(
        f"  {i+1}. {name} — {cnt} marta"
        for i, (name, cnt) in enumerate(data["popular_names"])
    ) or "  Ma'lumot yo'q"

    by_holiday = "\n".join(
        f"  {holiday_names.get(h, h)}: {cnt} ta"
        for h, cnt in data["by_holiday"]
    ) or "  Ma'lumot yo'q"

    text = (
        f"📊 *Statistika*\n\n"
        f"👤 Jami foydalanuvchilar: *{data['total_users']}*\n"
        f"📨 Jami so'rovlar: *{data['total_requests']}*\n"
        f"📅 Bugungi so'rovlar: *{data['today_requests']}*\n\n"
        f"🔤 Eng ko'p ishlatiladigan ismlar:\n{popular}\n\n"
        f"🎉 Bayram bo'yicha:\n{by_holiday}"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def template_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    template_index = int(query.data.split("_")[1]) - 1
    user_id = query.from_user.id
    user_sessions[user_id]["step"] = "name"
    user_sessions[user_id]["theme_index"] = template_index
    await query.message.reply_text(
        "✍️ *Ismni yozing:*\n_Masalan: Ali, Oyi, Qizalog'im..._",
        parse_mode='Markdown'
    )

def template_keyboard(holiday):
    max_template = 10 if holiday == "arafa" else 20
    keyboard = []
    row = []
    for i in range(1, max_template + 1):
        row.append(InlineKeyboardButton(str(i), callback_data=f"template_{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


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
            msg = (
                f"🎉 Bugun *{name}*!\nHayitingiz muborak! 🎊"
                if days == 0 else
                f"📅 Keyingi bayram:\n\n*{name}*\n🗓 {date}\n⏳ *{days} kun* qoldi"
            )
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
        theme_index = session.get("theme_index", 0)
        user_sessions[user_id]["step"] = "done"

        holiday_emoji = {"ramazon": "🌙", "qurbon": "🐑", "arafa": "🤲"}.get(holiday, "🎉")
        holiday_name  = {"ramazon": "Ramazon Hayiti", "qurbon": "Qurbon Hayiti", "arafa": "Arafa kuni"}.get(holiday, "Hayit")

        await update.message.reply_text(
            f"{holiday_emoji} *{name}*ga {holiday_name} tabrigi yaratilmoqda...",
            parse_mode='Markdown'
        )

        await save_request(user_id, name, holiday)

        try:
            file_id = await get_cached_file_id(name, holiday, theme_index)
            if file_id:
                msg = await context.bot.send_photo(chat_id=update.message.chat_id, photo=file_id)
                logger.info(f"Cache ishlatildi: {name}/{holiday}/{theme_index}")
            else:
                image_path = generate_card(name, holiday, theme_index)
                with open(image_path, 'rb') as photo:
                    msg = await context.bot.send_photo(chat_id=update.message.chat_id, photo=photo)
                os.remove(image_path)
                await save_cache(name, holiday, theme_index, msg.photo[-1].file_id)
        except Exception as e:
            logger.error(f"Rasm yaratishda xato: {e}")
            await update.message.reply_text("❌ Rasm yaratishda xato. Qaytadan urinib ko'ring.")
            return

        await update.message.reply_text(
            "✅ Tayyor! Yaqinlaringizga yuboring 💌",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Yana tabrik yaratish", callback_data="back_start")]
            ])
        )


async def holiday_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    holiday = query.data.split("_")[1]
    user_sessions[query.from_user.id] = {"step": "template", "holiday": holiday}
    await query.message.reply_text(
        "🎨 *Avval shablonlarni ko'ring:*\n👉 @Shablonlar_uchun\n\nKeyin quyidan tanlang:",
        reply_markup=template_keyboard(holiday)
    )


async def family_holiday_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    holiday = query.data.split("_")[1]
    user_sessions[query.from_user.id] = {"step": "template", "holiday": holiday}
    await query.message.reply_text(
        "🎨 *Avval shablonlarni ko'ring:*\n👉 @Shablonlar_uchunl\n\nKeyin quyidan tanlang:",
        reply_markup=template_keyboard(holiday)
    )


async def send_holiday_greetings(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().date()
    for key, holiday in HOLIDAYS.items():
        holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
        days_left = (holiday_date - today).days

        if days_left < 0 or days_left > 10:
            continue

        if days_left == 0:
            text = "🎉 Bugun bayram! /start bosib tabrik kartochkasi yarating!"
        else:
            names = {"ramazon": "🌙 Ramazon Hayiti", "qurbon": "🐑 Qurbon Hayiti", "arafa": "🤲 Arafa kuni"}
            text = f"📅 {names[holiday['type']]}ga *{days_left} kun* qoldi!"

        user_ids = await get_all_active_users()
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=user_id, text=text, parse_mode='Markdown')
                await asyncio.sleep(0.05)
            except Exception as e:
                if "blocked" in str(e).lower() or "deactivated" in str(e).lower():
                    await deactivate_user(user_id)
                else:
                    logger.error(f"Xato user {user_id}: {e}")


async def on_startup(app):
    await init_db()
    logger.info("Database ulandi ✅")


async def on_shutdown(app):
    await close_pool()
    logger.info("Database ulanishi yopildi")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(template_chosen, pattern="^template_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(holiday_chosen,       pattern="^holiday_"))
    app.add_handler(CallbackQueryHandler(family_holiday_chosen, pattern="^fholiday_"))
    app.add_handler(CallbackQueryHandler(start,                 pattern="^back_start$"))

    app.job_queue.run_daily(
        send_holiday_greetings,
        time=datetime.strptime("08:00", "%H:%M").time()
    )

    app.post_init     = on_startup
    app.post_shutdown = on_shutdown

    logger.info("Bot ishga tushdi! ✅")
    app.run_polling()


if __name__ == '__main__':
    main()