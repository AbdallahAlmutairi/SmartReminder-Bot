"""
bot/handlers.py
───────────────
Telegram command & message handlers using python-telegram-bot (v20+, async).
Wires user messages → NLP parser → Google Tasks/Calendar service.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from nlp.parser import ReminderParser
from services.google_tasks import GoogleTasksService
from config.settings import settings

logger = logging.getLogger(__name__)
parser = ReminderParser()


# ── /start ──────────────────────────────────────────────────────────────────
async def start_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome = (
        f"👋 أهلاً {user.first_name}!\n\n"
        "🤖 أنا بوت التذكيرات الذكي. أرسل لي جملة مثل:\n\n"
        "  • *ذكرني بموعد الطبيب الأحد الساعة 9 مساءً*\n"
        "  • *Remind me to call Ahmed tomorrow at 3 PM*\n\n"
        "وسأضيفها تلقائياً إلى Google Tasks! 📅\n\n"
        "📌 اكتب /connect لربط حساب Google أولاً."
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


# ── /help ───────────────────────────────────────────────────────────────────
async def help_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 *الأوامر المتاحة:*\n\n"
        "/start — رسالة الترحيب\n"
        "/connect — ربط حساب Google\n"
        "/tasks — عرض مهامك القادمة\n"
        "/help — هذه الرسالة\n\n"
        "💬 *أو فقط أرسل تذكيراً بالعربية أو الإنجليزية!*"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ── Natural Language Message Handler ────────────────────────────────────────
async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Main handler: parses free-text reminder → creates Google Task.
    """
    user_id = update.effective_user.id
    text = update.message.text

    await update.message.reply_text("🔍 جارٍ تحليل التذكير...")

    # 1. Parse with NLP engine
    result = parser.parse(text)

    if not result.is_parsed:
        await update.message.reply_text(
            "⚠️ لم أستطع تحديد التاريخ.\n"
            "جرّب صياغة مثل: *ذكرني بـ [الحدث] [اليوم] الساعة [الوقت]*",
            parse_mode="Markdown",
        )
        return

    # 2. Format confirmation message
    dt_str = result.datetime_obj.strftime("%A، %d %B %Y — %I:%M %p")
    conf_emoji = "✅" if result.confidence >= 0.7 else "⚠️"

    confirmation = (
        f"{conf_emoji} *تم تحليل التذكير:*\n\n"
        f"📌 *العنوان:* {result.title}\n"
        f"📅 *الموعد:* {dt_str}\n"
        f"🎯 *الدقة:* {int(result.confidence * 100)}%\n\n"
        "هل تريد حفظه في Google Tasks؟"
    )

    # 3. Inline keyboard for confirmation
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ حفظ", callback_data=f"save|{user_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel"),
        ]
    ])

    # Store parsed result in context for callback
    ctx.user_data["pending_reminder"] = result

    await update.message.reply_text(
        confirmation,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


# ── Callback: Save / Cancel ──────────────────────────────────────────────────
async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    action = query.data.split("|")[0]

    if action == "cancel":
        await query.edit_message_text("❌ تم الإلغاء.")
        return

    reminder = ctx.user_data.get("pending_reminder")
    if not reminder:
        await query.edit_message_text("⚠️ انتهت صلاحية التذكير، أعد الإرسال.")
        return

    # Attempt to save to Google Tasks
    try:
        service = GoogleTasksService(user_id=update.effective_user.id)
        task_id = await service.create_task(
            title=reminder.title,
            due=reminder.datetime_obj,
        )
        await query.edit_message_text(
            f"✅ تم الحفظ في Google Tasks!\n🆔 `{task_id}`",
            parse_mode="Markdown",
        )
    except Exception as exc:
        logger.error("Google Tasks error: %s", exc)
        await query.edit_message_text(
            "❌ فشل الحفظ. تأكد من ربط حساب Google عبر /connect"
        )
