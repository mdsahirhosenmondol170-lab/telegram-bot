import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ---------------- BOT TOKEN ----------------
TOKEN = "7814201774:AAFPHgEKFPnTU5U9dDcV0H0_9sO1P7BfNl4"   # ← তোমার বট টোকেন
CHANNEL = "https://t.me/PowerPointBreak"
GROUP = "https://t.me/PowerPointBreakConversion"

# ---------------- DATA STORE ----------------
giveaway_data = {}
welcome_text = "👋 Welcome {name} to PowerPointBreak Community!"

# ---------------- /HELP ----------------
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 <b>PowerPointBreak Bot — Commands</b>\n\n"
        "👋 <b>General</b>\n"
        "/start — Check if bot is online\n"
        "/help — Show this help\n"
        "/rules — Channel & Group links\n\n"
        "🎉 <b>Giveaway</b>\n"
        "/startgiveaway <minutes> <slots> [title] — Start a giveaway (Admin)\n"
        "/enter — Join active giveaway\n"
        "/status <id> — Show giveaway status\n"
        "/pick <id> — Pick winners (Admin)\n\n"
        "👋 <b>Welcome</b>\n"
        "/setwelcome <text> — Set welcome (use {name})\n"
        "/previewwelcome — Preview welcome\n"
        "/removewelcome — Remove welcome\n\n"
        "ℹ️ <i>Note:</i>\n"
        "• Giveaway entry only for members of Channel & Group.\n"
        "• Countdown updates every second with live progress bar.\n"
    )
    await update.message.reply_html(text)

# ---------------- /START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is online and running perfectly!")

# ---------------- /RULES ----------------
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"📢 Channel: {CHANNEL}\n💬 Group: {GROUP}\nStay connected for updates & giveaways!"
    await update.message.reply_text(text)

# ---------------- /SETWELCOME ----------------
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global welcome_text
    text = " ".join(context.args)
    if not text:
        return await update.message.reply_text("Usage: /setwelcome Welcome {name}!")
    welcome_text = text
    await update.message.reply_text("✅ Custom welcome message set!")

async def previewwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(welcome_text.replace("{name}", update.effective_user.first_name))

async def removewelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global welcome_text
    welcome_text = "👋 Welcome {name} to PowerPointBreak Community!"
    await update.message.reply_text("✅ Welcome reset to default.")

# ---------------- GIVEAWAY SYSTEM ----------------
async def startgiveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /startgiveaway <minutes> <slots> [title]")
    minutes = int(context.args[0])
    slots = int(context.args[1])
    title = " ".join(context.args[2:]) if len(context.args) > 2 else "Exclusive Giveaway 🎁"
    end_time = datetime.now() + timedelta(minutes=minutes)
    gid = len(giveaway_data) + 1
    giveaway_data[gid] = {"end_time": end_time, "slots": slots, "joined": [], "title": title}

    kb = [[InlineKeyboardButton("🎉 Join Giveaway", callback_data=f"join_{gid}")]]
    msg = await update.message.reply_text(
        f"🎁 <b>{title}</b>\nEnds in {minutes} minutes.\nSlots: {slots}\n\nJoin now!",
        parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb)
    )
    asyncio.create_task(countdown_progress(context.bot, msg, gid, minutes))

async def countdown_progress(bot, msg, gid, minutes):
    end_time = giveaway_data[gid]["end_time"]
    total = minutes * 60
    while True:
        remain = (end_time - datetime.now()).total_seconds()
        if remain <= 0:
            await msg.edit_text("🎉 Giveaway Ended! Winners will be announced soon!")
            break
        pct = int((1 - remain / total) * 100)
        bar = "▓" * (pct // 5) + "░" * (20 - pct // 5)
        await msg.edit_text(
            f"🎁 <b>{giveaway_data[gid]['title']}</b>\nProgress: [{bar}] {pct}%\nTime left: {int(remain)//60}m {int(remain)%60}s",
            parse_mode="HTML"
        )
        await asyncio.sleep(1)

# ---------------- JOIN BUTTON ----------------
async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    gid = int(q.data.split("_")[1])
    user = q.from_user
    if user.id in giveaway_data[gid]["joined"]:
        return await q.edit_message_text("⚠️ You already joined this giveaway!")
    giveaway_data[gid]["joined"].append(user.id)
    await q.edit_message_text(f"✅ {user.first_name} joined successfully! 🎉")

# ---------------- MAIN ----------------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("setwelcome", setwelcome))
app.add_handler(CommandHandler("previewwelcome", previewwelcome))
app.add_handler(CommandHandler("removewelcome", removewelcome))
app.add_handler(CommandHandler("startgiveaway", startgiveaway))
app.add_handler(CallbackQueryHandler(join_callback, pattern="^join_"))

print("✅ PowerPointBreak Bot running...")
app.run_polling()
