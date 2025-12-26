import requests
import telebot
from telebot import types
from html import escape
import logging
import datetime
import re # Regular expression for 'get' command parsing

# ------------------------------------------------- CONFIGURATION -------------------------------------------------
# **IMPORTANT**: Replace these placeholders with your actual values
BOT_TOKEN = "8571412229:AAHJllUbzGHX-EPwmwI6Z_WIsLd_En8mLv0" # Use the token from Visit-Bot.py
YOUR_BOT_USERNAME = "@TCPBOTALL_BOT"     # WITHOUT @ NAME, e.g., 'MyAwesomeBot'

DEVELOPER_NAME = "WAHAB"
CREDIT = "WAHAB"
OWNER_NAME = "WAHAB"
OWNER_URL = "WAHAB"

# GROUPS & CHANNEL (From Visit-Bot.py)
GROUP_1 = "PAIDSOUCRECODEX"
GROUP_2 = "theroshancodex07chatgroup"
CHANNEL = "theroshancodex"

# ------------------------------------------------- APIS ----------------------------------------------------------
ULTRA_API_URL = "https://checkregion-api.vercel.app/region?uid={uid}"
BANCHECK_API_URL = "https://ff.garena.com/api/antihack/check_banned?lang=en&uid={uid}"
API_VISIT_BASE = "https://spamxvisit-wotaxxdev-api.vercel.app/visits?uid={uid}&region=ind"
# This API is used for both /cklike and get command
API_INFO_URL = "http://danger-info-alpha.vercel.app/accinfo?uid={uid}&key=DANGERxINFO"
# -----------------------------------------------------------------------------------------------------------------

# INITIALIZE BOT
# Using Markdown as the primary parse mode for consistent style
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Headers for Ban Check API
BANCHECK_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'authority': 'ff.garena.com',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'referer': 'https://ff.garena.com/en/support/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-requested-with': 'B6FksShzIgjfrYImLpTsadjS86sddhFH',
}


# ------------------------------------------------- UTILITY FUNCTIONS ---------------------------------------------

def sanitize_markdown(text):
    """Removes Markdown special characters for safe message display."""
    if text is None:
        return "N/A"
    if not isinstance(text, str):
        text = str(text)
    # Escape characters used by Telegram Markdown V1
    return text.replace("*", "").replace("_", "").replace("[", "").replace("`", "").strip()

def is_valid_uid(uid: str) -> bool:
    """Checks if UID is a valid length of digits."""
    return uid.isdigit() and 8 <= len(uid) <= 11

def convert_ban_period_to_status(period_value):
    """Converts the ban check period value to a formatted status string."""
    try:
        period = int(period_value)
    except:
        return "UNKNOWN"
    return "NOT BANNED ✅" if period == 0 else "BANNED ❌"

def convert_time(ts):
    """Converts a Unix timestamp to formatted date and time strings."""
    try:
        ts = int(ts)
        # Convert timestamp to a readable format
        dt = datetime.datetime.utcfromtimestamp(ts)
        # Custom format to match the original style
        return dt.strftime("%d %B %Y").upper(), dt.strftime("%H:%M:%S")
    except:
        return "N/A", "N/A"

def create_promo_markup(add_me_button=False):
    """Creates the inline keyboard with promotional and optional 'Add Me' links."""
    markup = types.InlineKeyboardMarkup()
    # First row: Join Groups
    markup.row(
        types.InlineKeyboardButton("JOIN GROUP", url=f"https://t.me/theroshancodex07chatgroup1"),
        types.InlineKeyboardButton("JOIN GROUP", url=f"https://t.me/theroshancodex07chatgroup1")
    )
    # Second row: Join Channel
    markup.row(types.InlineKeyboardButton("JOIN CHANNEL", url=f"https://t.me/THEROSHANCODEX"))
    
    # Optional 'Add Me' button (from BAN_CHECK_BY_YASH.py)
    if add_me_button:
        markup.row(
            types.InlineKeyboardButton(
                text="➕ ADD ME TO YOUR GROUP",
                url=f"http://t.me/{YOUR_BOT_USERNAME}?startgroup=start"
            )
        )
        
    return markup


# ------------------------------------------------- HANDLERS ------------------------------------------------------

# 🧩 START & HELP COMMAND
@bot.message_handler(commands=['start', 'help'])
def start_handler(message):
    chat_id = message.chat.id
    
    msg_parts = [
        f"👋 HELLO {message.from_user.first_name.upper()}!\n\n",
        "━━━━━━━━━━━━━━━━━━━━\n",
        "        ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅꜱ\n",
        "━━━━━━━━━━━━━━━━━━━━\n",
        "`/visit <region> <uid>`\n",
        "`/bancheck <uid>`\n",
        "`/cklike <region> <uid>`\n",
        "`get <region> <uid>`\n",
        "`get <uid>`\n\n",
        "━━━━━━━━━━━━━━━━━━━━\n",
        "        ᴇxᴀᴍᴘʟᴇꜱ\n",
        "━━━━━━━━━━━━━━━━━━━━\n",
        "`/visit ind 2314978683`\n",
        "`/bancheck 2919267964`\n",
        "`/cklike ind 2314978683`\n",
        "`get ind 2314978683`\n",
        "`get 2314978683`\n\n",
        "━━━━━━━━━━━━━━━━━━━━\n",
        f"👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: {DEVELOPER_NAME}\n",
        f"❤️ ᴄʀᴇᴅɪᴛ: {CREDIT}\n",
        "━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    # Use the promotional markup with the 'Add Me' button
    bot.send_message(chat_id, "".join(msg_parts), reply_markup=create_promo_markup(add_me_button=True))

# 🧭 /VISIT COMMAND (UPDATED FOR NEW API RESPONSE)
@bot.message_handler(commands=['visit'])
def visit_command(message):
    chat_id = message.chat.id
    args = message.text.split()[1:]
    final_markup = create_promo_markup()

    # Usage check
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **ᴜꜱᴀɢᴇ:** `/visit <region> <uid>`", parse_mode="Markdown")
        return

    region, uid = args[0], args[1]

    processing = bot.reply_to(
        message,
        f"⏳ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ᴠɪꜱɪᴛ ꜰᴏʀ `{uid}`...",
        parse_mode="Markdown"
    )

    try:
        # API CALL
        res = requests.get(f"{API_VISIT_BASE}/{region}/{uid}", timeout=10)

        if res.status_code != 200:
            bot.edit_message_text(
                f"❌ ᴀᴘɪ ꜰᴀɪʟᴇᴅ ({res.status_code})",
                chat_id,
                processing.message_id,
                reply_markup=final_markup
            )
            return

        data = res.json()

        # EXTRACT DATA FROM NEW API RESPONSE
        nickname = sanitize_markdown(data.get("nickname", "N/A"))
        fetched_uid = data.get("uid", "N/A")
        success = data.get("success", 0)
        fail = data.get("fail", 0)
        level = data.get("level", "N/A")
        likes = data.get("likes", 0)
        total = success + fail  # Calculate total visits

        # Format large numbers with commas
        formatted_likes = "{:,}".format(likes) if likes != "N/A" else "N/A"

        # Final message with new data
        msg = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "        ᴠɪꜱɪᴛ ʀᴇꜱᴜʟᴛ\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 ɴᴀᴍᴇ: **{nickname}**\n"
            f"🆔 ᴜɪᴅ: `{fetched_uid}`\n"
            f"🎯 ʟᴇᴠᴇʟ: **{level}**\n"
            f"❤️ ʟɪᴋᴇꜱ: **{formatted_likes}**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "        ᴠɪꜱɪᴛ ᴅᴀᴛᴀ\n"
            "━━━━━━━━━━━━━━━━━━━━\n"       
            f"✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ᴠɪꜱɪᴛꜱ: **{success}**\n"
            f"❌ ꜰᴀɪʟᴇᴅ ᴠɪꜱɪᴛꜱ: **{fail}**\n"
            f"📊 ᴛᴏᴛᴀʟ ᴠɪꜱɪᴛꜱ: **{total}**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: **{DEVELOPER_NAME}**\n"
            f"❤️ ᴄʀᴇᴅɪᴛ: {CREDIT}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
        )

        bot.edit_message_text(
            msg,
            chat_id,
            processing.message_id,
            reply_markup=final_markup,
            parse_mode="Markdown"
        )

    except requests.exceptions.RequestException as e:
        bot.edit_message_text(
            f"❌ ɴᴇᴛᴡᴏʀᴋ/ᴛɪᴍᴇᴏᴜᴛ ᴇʀʀᴏʀ:\n`{sanitize_markdown(str(e))}`",
            chat_id,
            processing.message_id,
            reply_markup=final_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ:\n`{sanitize_markdown(str(e))}`",
            chat_id,
            processing.message_id,
            reply_markup=final_markup,
            parse_mode="Markdown"
        )
        
# 🔒 /BANCHECK COMMAND (Combined from BAN_CHECK_BY_YASH.py and Visit-Bot.py design)
@bot.message_handler(commands=['bancheck'])
def bancheck_handler(message):
    chat_id = message.chat.id
    final_markup = create_promo_markup(add_me_button=True)

    try:
        parts = message.text.strip().split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ ᴜꜱᴀɢᴇ: `/bancheck <UID>`\nᴇxᴀᴍᴘʟᴇ: `/bancheck 2919267964`")
            return

        uid = parts[1].strip()
        if not is_valid_uid(uid):
            bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ (8-11 ᴅɪɢɪᴛꜱ)!")
            return

        processing = bot.reply_to(message, f"⏳ ᴄʜᴇᴄᴋɪɴɢ ʙᴀɴ ꜱᴛᴀᴛᴜꜱ ꜰᴏʀ ᴜɪᴅ: `{uid}`", parse_mode="Markdown")

        nickname, region = "ɴ/ᴀ", "ɴ/ᴀ"
        try:
            # 1. Fetch Nickname and Region
            resp = requests.get(ULTRA_API_URL.format(uid=uid), timeout=10)
            if resp.status_code == 200:
                j = resp.json()
                nickname = sanitize_markdown(j.get("nickname") or j.get("name"))
                region = sanitize_markdown(j.get("region") or j.get("server"))
        except Exception as e:
            logger.warning(f"Region API failed for {uid}: {e}")

        ban_status_text = "ᴇʀʀᴏʀ"
        try:
            # 2. Fetch Ban Status
            ban_resp = requests.get(BANCHECK_API_URL.format(uid=uid), headers=BANCHECK_HEADERS, timeout=10)
            if ban_resp.status_code == 200:
                data = ban_resp.json().get("data", {})
                period = data.get("period", None)
                ban_status_text = convert_ban_period_to_status(period)
            else:
                ban_status_text = f"ᴀᴘɪ ᴇʀʀᴏʀ ({ban_resp.status_code})"
        except Exception as e:
            logger.error(f"Ban Check API failed for {uid}: {e}")
            ban_status_text = "ʀᴇǫᴜᴇꜱᴛ ꜰᴀɪʟᴇᴅ"

        # 3. Format Final Message
        msg = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "        ʙᴀɴ ᴄʜᴇᴄᴋ ʀᴇꜱᴜʟᴛ\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 ɴᴀᴍᴇ: **{nickname}**\n"
            f"🆔 ᴜɪᴅ: `{uid}`\n"
            f"🌍 ʀᴇɢɪᴏɴ: **{region}**\n"
            f"🛡️ ꜱᴛᴀᴛᴜꜱ: **{ban_status_text}**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: **{DEVELOPER_NAME}**\n"
            f"❤️ ᴄʀᴇᴅɪᴛ: {CREDIT}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
        )

        bot.edit_message_text(msg, chat_id=processing.chat.id, message_id=processing.message_id,
                              reply_markup=final_markup)

    except Exception as e:
        logger.error(f"General error in bancheck: {e}")
        bot.reply_to(message, f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: `{sanitize_markdown(str(e))}`", reply_markup=final_markup)

# ❤️ /CKLIKE COMMAND (New command to check 'liked' count)
@bot.message_handler(commands=['cklike'])
def cklike_command(message):
    chat_id = message.chat.id
    final_markup = create_promo_markup()

    try:
        args = message.text.split()[1:]

        if len(args) != 2:
            bot.reply_to(
                message,
                "⚠️ ᴜꜱᴀɢᴇ: `/cklike <REGION> <UID>`\nᴇxᴀᴍᴘʟᴇ: `/cklike ind 2314978683`"
            )
            return

        region, uid = args[0], args[1]
        
        processing = bot.reply_to(
            message,
            f"⏳ ꜰᴇᴛᴄʜɪɴɢ ʟɪᴋᴇ ᴄᴏᴜɴᴛ ꜰᴏʀ `{uid}` ɪɴ `{region}`...",
            parse_mode="Markdown"
        )
        
        # API FETCH using the already defined API_INFO_URL
        res = requests.get(API_INFO_URL.format(uid=uid, region=region), timeout=10)
        
        if res.status_code != 200:
            bot.edit_message_text(
                f"❌ ᴀᴘɪ ꜰᴀɪʟᴇᴅ ({res.status_code})", 
                chat_id, 
                processing.message_id, 
                reply_markup=final_markup
            )
            return
            
        data = res.json()
        
        # Check if basicInfo is missing (API error or invalid ID/region)
        if "basicInfo" not in data:
            error_msg = data.get("error", "ɪɴᴠᴀʟɪᴅ ᴜɪᴅ ᴏʀ ʀᴇɢɪᴏɴ")
            bot.edit_message_text(
                f"❌ ᴇʀʀᴏʀ: `{sanitize_markdown(error_msg)}`", 
                chat_id, 
                processing.message_id,
                reply_markup=final_markup
            )
            return

        basic_info = data["basicInfo"]
        s = sanitize_markdown # Alias for convenience

        nickname = s(basic_info.get("nickname"))
        region_ = s(basic_info.get("region"))
        level = s(basic_info.get("level"))
        liked = s(basic_info.get("liked"))

        # FINAL RESULT
        final = f"""
━━━━━━━━━━━━━━━━━━━━
        ʟɪᴋᴇ ᴄᴏᴜɴᴛ ʀᴇꜱᴜʟᴛ
━━━━━━━━━━━━━━━━━━━━

👤 ɴɪᴄᴋɴᴀᴍᴇ: **{nickname}**
🌍 ʀᴇɢɪᴏɴ: **{region_}**
🔰 ʟᴇᴠᴇʟ: **{level}**
❤️ ʟɪᴋᴇꜱ: **{liked}**

━━━━━━━━━━━━━━━━━━━━
👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: **{DEVELOPER_NAME}**
❤️ ᴄʀᴇᴅɪᴛ: {CREDIT}
━━━━━━━━━━━━━━━━━━━━
"""

        bot.edit_message_text(
            final, 
            chat_id, 
            processing.message_id,
            reply_markup=final_markup,
            parse_mode="Markdown"
        )

    except requests.exceptions.RequestException as e:
        bot.edit_message_text(
            f"❌ ɴᴇᴛᴡᴏʀᴋ/ᴛɪᴍᴇᴏᴜᴛ ᴇʀʀᴏʀ: `{sanitize_markdown(str(e))}`", 
            chat_id, 
            processing.message_id,
            reply_markup=final_markup
        )
    except Exception as e:
        logger.error(f"General error in cklike_command: {e}")
        bot.edit_message_text(f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: `{sanitize_markdown(str(e))}`", chat_id, processing.message_id, reply_markup=final_markup)

# ----------------------------------------------------------------------------
# GET COMMANDS
# 1) get <REGION> <UID>  -> searches the given region
# 2) get <UID>          -> auto-locked to IND
# ----------------------------------------------------------------------------

# Handler for: get <REGION> <UID>
@bot.message_handler(regexp=r'^[gG][eE][tT]\s+([a-zA-Z]{2,4})\s+(\d+)$')
def get_info_with_region(message):
    chat_id = message.chat.id
    final_markup = create_promo_markup()
    
    try:
        match = re.search(r'^[gG][eE][tT]\s+([a-zA-Z]{2,4})\s+(\d+)$', message.text.strip())
        if not match:
            bot.reply_to(message, "⚠️ ᴜꜱᴀɢᴇ: `get <REGION> <UID>`\nᴇxᴀᴍᴘʟᴇ: `get ind 2314978683`")
            return

        region = match.group(1).upper()
        uid = match.group(2)

        processing = bot.reply_to(message, f"🔍 ꜱᴇᴀʀᴄʜɪɴɢ `{uid}` ɪɴ `{region}`...", parse_mode="Markdown")

        res = requests.get(API_INFO_URL.format(uid=uid, region=region), timeout=15)
        if res.status_code != 200:
            bot.edit_message_text(f"❌ ᴀᴘɪ ꜰᴀɪʟᴇᴅ ({res.status_code})", chat_id, processing.message_id, reply_markup=final_markup)
            return

        data = res.json()
        if "basicInfo" not in data:
            bot.edit_message_text("❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ ᴏʀ ʀᴇɢɪᴏɴ", chat_id, processing.message_id, reply_markup=final_markup)
            return

        basic = data["basicInfo"]
        profile = data.get("profileInfo", {})
        clan = data.get("clanBasicInfo", {})
        captain = data.get("captainBasicInfo", {})
        pet = data.get("petInfo", {})
        social = data.get("socialInfo", {})
        
        s = sanitize_markdown 
        
        # Convert timestamps
        created_date, created_time = convert_time(basic.get("createAt", 0))
        last_login_date, last_login_time = convert_time(basic.get("lastLoginAt", 0))
        leader_join_date, leader_join_time = convert_time(captain.get("createAt", 0))
        leader_last_login_date, leader_last_login_time = convert_time(captain.get("lastLoginAt", 0))

        msg = f"""
━━━━━━━━━━━━━━━━━━━━
        ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ
━━━━━━━━━━━━━━━━━━━━

👤 **ʙᴀꜱɪᴄ ɪɴꜰᴏ**
├─ ɴᴀᴍᴇ: {s(basic.get("nickname"))}
├─ ᴜɪᴅ: {s(basic.get("accountId"))}
├─ ʟᴇᴠᴇʟ: {s(basic.get("level"))}
├─ ᴇxᴘ: {s(basic.get("exp"))}
├─ ʀᴇɢɪᴏɴ: {s(basic.get("region"))}
├─ ʟɪᴋᴇꜱ: {s(basic.get("liked"))}
├─ ʜᴏɴᴏʀ ꜱᴄᴏʀᴇ: {s(data.get("creditScoreInfo",{}).get("creditScore"))}
├─ ᴛɪᴛʟᴇ: {s(basic.get("title"))}
└─ ꜱɪɢɴᴀᴛᴜʀᴇ: {s(social.get("signature"))}

🏆 **ᴀᴄᴄᴏᴜɴᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ**
├─ ɢᴀᴍᴇ ᴠᴇʀꜱɪᴏɴ: {s(basic.get("releaseVersion"))}
├─ ʙʀ ʀᴀɴᴋ: {s(basic.get("rank"))}
├─ ʙʀ ᴍᴀx ʀᴀɴᴋ: {s(basic.get("maxRank"))}
├─ ᴄꜱ ʀᴀɴᴋ: {s(basic.get("csRank"))}
├─ ᴄꜱ ᴍᴀx ʀᴀɴᴋ: {s(basic.get("csMaxRank"))}
├─ ᴄʀᴇᴀᴛᴇᴅ ᴅᴀᴛᴇ: {created_date}
├─ ᴛɪᴍᴇ: {created_time}
├─ ʟᴀꜱᴛ ʟᴏɢɪɴ: {last_login_date}
└─ ᴛɪᴍᴇ: {last_login_time}

👕 **ᴄʜᴀʀᴀᴄᴛᴇʀ ᴀᴘᴘᴇᴀʀᴀɴᴄᴇ**
├─ ᴀᴠᴀᴛᴀʀ ɪᴅ: {s(profile.get("avatarId"))}
├─ ʙᴀɴɴᴇʀ ɪᴅ: {s(basic.get("bannerId"))}
└─ ʙᴀᴅɢᴇ ɪᴅ: {s(basic.get("badgeId"))}

🐾 **ᴘᴇᴛ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**
├─ ᴘᴇᴛ ʟᴇᴠᴇʟ: {s(pet.get("level"))}
├─ ᴘᴇᴛ ᴇxᴘ: {s(pet.get("exp"))}
└─ ᴘᴇᴛ ɪᴅ: {s(pet.get("id"))}

🏰 **ɢᴜɪʟᴅ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**
├─ ɢᴜɪʟᴅ ɴᴀᴍᴇ: {s(clan.get("clanName", "None"))}
├─ ɢᴜɪʟᴅ ɪᴅ: {s(clan.get("clanId"))}
├─ ɢᴜɪʟᴅ ʟᴇᴠᴇʟ: {s(clan.get("clanLevel"))}
└─ ᴍᴇᴍʙᴇʀꜱ: {s(clan.get("memberNum"))}

🧑‍✈️ **ʟᴇᴀᴅᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**
├─ ɴᴀᴍᴇ: {s(captain.get("nickname"))}
├─ ᴜɪᴅ: {s(captain.get("accountId"))}
├─ ʟᴇᴠᴇʟ: {s(captain.get("level"))}
├─ ᴇxᴘ: {s(captain.get("exp"))}
├─ ᴄʀᴇᴀᴛᴇᴅ ᴅᴀᴛᴇ: {leader_join_date}
├─ ᴛɪᴍᴇ: {leader_join_time}
├─ ʟᴀꜱᴛ ʟᴏɢɪɴ: {leader_last_login_date}
├─ ᴛɪᴍᴇ: {leader_last_login_time}
├─ ᴛɪᴛʟᴇ: {s(captain.get("title"))}
├─ ʙʀ ᴘᴏɪɴᴛꜱ: {s(captain.get("rankingPoints"))}
└─ ᴄꜱ ᴘᴏɪɴᴛꜱ: {s(captain.get("csRankingPoints"))}

🗺️ **ᴘᴜʙʟɪᴄ ᴄʀᴀꜰᴛʟᴀɴᴅ ᴍᴀᴘꜱ**: Not Found

━━━━━━━━━━━━━━━━━━━━
👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: **{DEVELOPER_NAME}**
❤️ ᴄʀᴇᴅɪᴛ: {CREDIT}
━━━━━━━━━━━━━━━━━━━━
"""
        bot.edit_message_text(msg, chat_id, processing.message_id, reply_markup=final_markup)

    except Exception as e:
        bot.edit_message_text(
            f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: `{sanitize_markdown(str(e))}`",
            chat_id,
            processing.message_id,
            reply_markup=final_markup
        )

# Handler for: get <UID>  (auto region = IND)
@bot.message_handler(regexp=r'^[gG][eE][tT]\s+(\d+)$')
def get_info_auto_region(message):
    chat_id = message.chat.id
    final_markup = create_promo_markup()
    
    try:
        # Regex: get <UID>
        match = re.search(r'^[gG][eE][tT]\s+(\d+)$', message.text.strip())
        
        if not match:
            bot.reply_to(message, "⚠️ ᴜꜱᴀɢᴇ: `get <UID>`\nᴇxᴀᴍᴘʟᴇ: `get 2314978683`")
            return

        uid = match.group(1)
        region = "IND"  # AUTO LOCKED REGION

        processing = bot.reply_to(
            message,
            f"🔍 ꜱᴇᴀʀᴄʜɪɴɢ `{uid}` ɪɴ `IND`...",
            parse_mode="Markdown"
        )

        res = requests.get(API_INFO_URL.format(uid=uid, region=region), timeout=15)
        if res.status_code != 200:
            bot.edit_message_text(f"❌ ᴀᴘɪ ꜰᴀɪʟᴇᴅ ({res.status_code})", chat_id, processing.message_id, reply_markup=final_markup)
            return

        data = res.json()
        if "basicInfo" not in data:
            bot.edit_message_text(
                "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ ᴏʀ ʀᴇɢɪᴏɴ",
                chat_id,
                processing.message_id,
                reply_markup=final_markup
            )
            return

        basic = data["basicInfo"]
        profile = data.get("profileInfo", {})
        clan = data.get("clanBasicInfo", {})
        captain = data.get("captainBasicInfo", {})
        pet = data.get("petInfo", {})
        social = data.get("socialInfo", {})
        
        s = sanitize_markdown 
        
        # Convert timestamps
        created_date, created_time = convert_time(basic.get("createAt", 0))
        last_login_date, last_login_time = convert_time(basic.get("lastLoginAt", 0))
        leader_join_date, leader_join_time = convert_time(captain.get("createAt", 0))
        leader_last_login_date, leader_last_login_time = convert_time(captain.get("lastLoginAt", 0))

        msg = f"""
━━━━━━━━━━━━━━━━━━━━
        ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ
━━━━━━━━━━━━━━━━━━━━

👤 **ʙᴀꜱɪᴄ ɪɴꜰᴏ**
├─ ɴᴀᴍᴇ: {s(basic.get("nickname"))}
├─ ᴜɪᴅ: {s(basic.get("accountId"))}
├─ ʟᴇᴠᴇʟ: {s(basic.get("level"))}
├─ ᴇxᴘ: {s(basic.get("exp"))}
├─ ʀᴇɢɪᴏɴ: IND (ᴀᴜᴛᴏ)
├─ ʟɪᴋᴇꜱ: {s(basic.get("liked"))}
├─ ʜᴏɴᴏʀ ꜱᴄᴏʀᴇ: {s(data.get("creditScoreInfo",{}).get("creditScore"))}
├─ ᴛɪᴛʟᴇ: {s(basic.get("title"))}
└─ ꜱɪɢɴᴀᴛᴜʀᴇ: {s(social.get("signature"))}

🏆 **ᴀᴄᴄᴏᴜɴᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ**
├─ ɢᴀᴍᴇ ᴠᴇʀꜱɪᴏɴ: {s(basic.get("releaseVersion"))}
├─ ʙʀ ʀᴀɴᴋ: {s(basic.get("rank"))}
├─ ʙʀ ᴍᴀx ʀᴀɴᴋ: {s(basic.get("maxRank"))}
├─ ᴄꜱ ʀᴀɴᴋ: {s(basic.get("csRank"))}
├─ ᴄꜱ ᴍᴀx ʀᴀɴᴋ: {s(basic.get("csMaxRank"))}
├─ ᴄʀᴇᴀᴛᴇᴅ ᴅᴀᴛᴇ: {created_date}
├─ ᴛɪᴍᴇ: {created_time}
├─ ʟᴀꜱᴛ ʟᴏɢɪɴ: {last_login_date}
└─ ᴛɪᴍᴇ: {last_login_time}

👕 **ᴄʜᴀʀᴀᴄᴛᴇʀ ᴀᴘᴘᴇᴀʀᴀɴᴄᴇ**
├─ ᴀᴠᴀᴛᴀʀ ɪᴅ: {s(profile.get("avatarId"))}
├─ ʙᴀɴɴᴇʀ ɪᴅ: {s(basic.get("bannerId"))}
└─ ʙᴀᴅɢᴇ ɪᴅ: {s(basic.get("badgeId"))}

🐾 **ᴘᴇᴛ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**
├─ ᴘᴇᴛ ʟᴇᴠᴇʟ: {s(pet.get("level"))}
├─ ᴘᴇᴛ ᴇxᴘ: {s(pet.get("exp"))}
└─ ᴘᴇᴛ ɪᴅ: {s(pet.get("id"))}

🏰 **ɢᴜɪʟᴅ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**
├─ ɢᴜɪʟᴅ ɴᴀᴍᴇ: {s(clan.get("clanName", "None"))}
├─ ɢᴜɪʟᴅ ɪᴅ: {s(clan.get("clanId"))}
├─ ɢᴜɪʟᴅ ʟᴇᴠᴇʟ: {s(clan.get("clanLevel"))}
└─ ᴍᴇᴍʙᴇʀꜱ: {s(clan.get("memberNum"))}

🧑‍✈️ **ʟᴇᴀᴅᴇʀ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**
├─ ɴᴀᴍᴇ: {s(captain.get("nickname"))}
├─ ᴜɪᴅ: {s(captain.get("accountId"))}
├─ ʟᴇᴠᴇʟ: {s(captain.get("level"))}
├─ ᴇxᴘ: {s(captain.get("exp"))}
├─ ᴄʀᴇᴀᴛᴇᴅ ᴅᴀᴛᴇ: {leader_join_date}
├─ ᴛɪᴍᴇ: {leader_join_time}
├─ ʟᴀꜱᴛ ʟᴏɢɪɴ: {leader_last_login_date}
├─ ᴛɪᴍᴇ: {leader_last_login_time}
├─ ᴛɪᴛʟᴇ: {s(captain.get("title"))}
├─ ʙʀ ᴘᴏɪɴᴛꜱ: {s(captain.get("rankingPoints"))}
└─ ᴄꜱ ᴘᴏɪɴᴛꜱ: {s(captain.get("csRankingPoints"))}

🗺️ **ᴘᴜʙʟɪᴄ ᴄʀᴀꜰᴛʟᴀɴᴅ ᴍᴀᴘꜱ**: Not Found

━━━━━━━━━━━━━━━━━━━━
👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: **{DEVELOPER_NAME}**
❤️ ᴄʀᴇᴅɪᴛ: {CREDIT}
━━━━━━━━━━━━━━━━━━━━
"""

        bot.edit_message_text(msg, chat_id, processing.message_id, reply_markup=final_markup)

    except Exception as e:
        bot.edit_message_text(
            f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ: `{sanitize_markdown(str(e))}`",
            chat_id,
            processing.message_id,
            reply_markup=final_markup
        )
        
        
if __name__ == "__main__":
    print("🤖 ᴍᴇʀɢᴇᴅ ʙᴏᴛ ꜱᴛᴀʀᴛɪɴɢ...")
    # Use infinity_polling for a robust Telegram bot setup
    bot.infinity_polling()