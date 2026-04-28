import random
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from waifu import application, BOT_USERNAME, GROUP_ID, PHOTO_URL, SUPPORT_CHAT, UPDATE_CHAT
from waifu import pm_users as _pm

WELCOME = (
    "✨ <b>Welcome to WaifuHub Verse!</b> ✨\n\n"
    "🌸 <i>Where every message brings a new waifu...</i>\n\n"
    "⚡ <b>How to Play:</b>\n"
    "┣ Characters drop randomly in groups\n"
    "┣ Type /guess to claim them\n"
    "┣ Build your ultimate harem collection\n"
    "┗ Flex on everyone with rare waifus!\n\n"
    "💎 <b>Rarities:</b>\n"
    "┣ ⚪ Common  🟢 Medium  🟣 Rare\n"
    "┣ 🟡 Legendary  💮 Special Edition\n"
    "┗ 🔞 Extreme  <i>(rarest of all!)</i>\n\n"
    "🎴 <i>Add me to your group and let the hunt begin!</i> 🎴"
)

HELP = (
    "📖 <b>Commands</b>\n\n"
    "<b>🎮 Game</b>\n"
    "/guess — Claim the active character\n"
    "/harem — Your collection (paginated)\n"
    "/fav [id] — Set favourite character\n"
    "/check [id] — Check character details by ID\n"
    "/profile — Your stats & level\n\n"
    "<b>💰 Economy</b>\n"
    "/daily — Claim daily coins\n"
    "/balance — Check your coins\n"
    "/market — Browse listings\n"
    "/sell [id] [price] — List a character\n"
    "/buy [listing_id] — Buy from market\n\n"
    "<b>⚔️ Social</b>\n"
    "/ship @user — Find love compatibility 💕\n"
    "/trade [char_id] [their_char_id] — Trade (reply to user)\n"
    "/gift [char_id] — Gift a character (reply to user)\n"
    "/duel — Challenge someone to a duel (reply to user)\n\n"
    "<b>📊 Leaderboards</b>\n"
    "/top — Top collectors\n"
    "/ctop — This group's top\n"
    "/TopGroups — Most active groups\n\n"
    "<b>⚙️ Settings</b>\n"
    "/changetime [n] — Drop every n messages (admin)\n"
    "/resettime — Reset to default (admin)\n"
)


def _kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{BOT_USERNAME}?startgroup=new")],
        [
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT}"),
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{UPDATE_CHAT}"),
        ],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ])


async def start(update: Update, context: CallbackContext) -> None:
    u = update.effective_user
    existing = await _pm.find_one({"_id": u.id})
    if existing is None:
        await _pm.insert_one({"_id": u.id, "first_name": u.first_name, "username": u.username})
        try:
            await context.bot.send_message(
                GROUP_ID,
                f"🆕 New user: <a href='tg://user?id={u.id}'>{escape(u.first_name)}</a>",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    else:
        patch = {}
        if existing.get("first_name") != u.first_name: patch["first_name"] = u.first_name
        if existing.get("username")   != u.username:   patch["username"]   = u.username
        if patch:
            await _pm.update_one({"_id": u.id}, {"$set": patch})

    photo = random.choice(PHOTO_URL) if PHOTO_URL else None
    caption = WELCOME if update.effective_chat.type == "private" else "🎴 I'm alive! DM me for info."

    if photo:
        await context.bot.send_photo(
            update.effective_chat.id, photo=photo,
            caption=caption, reply_markup=_kb(), parse_mode=ParseMode.HTML,
        )
    else:
        await context.bot.send_message(
            update.effective_chat.id,
            text=caption, reply_markup=_kb(), parse_mode=ParseMode.HTML,
        )


async def button(update: Update, context: CallbackContext) -> None:
    q = update.callback_query
    await q.answer()

    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]])

    try:
        if q.data == "help":
            await q.edit_message_caption(caption=HELP, reply_markup=back_kb, parse_mode=ParseMode.HTML)
        elif q.data == "back":
            await q.edit_message_caption(caption=WELCOME, reply_markup=_kb(), parse_mode=ParseMode.HTML)
    except Exception:
        try:
            if q.data == "help":
                await q.edit_message_text(HELP, reply_markup=back_kb, parse_mode=ParseMode.HTML)
            elif q.data == "back":
                await q.edit_message_text(WELCOME, reply_markup=_kb(), parse_mode=ParseMode.HTML)
        except Exception:
            pass


application.add_handler(CommandHandler("start", start, block=False))
application.add_handler(CallbackQueryHandler(button, pattern=r"^(help|back)$", block=False))
