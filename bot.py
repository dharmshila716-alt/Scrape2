import os
import re
import time
import random
from datetime import datetime
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Credentials
API_ID = 34382392
API_HASH = "a325f2ae97b1d748b24641247b9965a6"
BOT_TOKEN = "8631805640:AAHWBIPq5YUeWFYmNw3AfVPFepQDJX7vkK0"
SESSION_STRING = "BQIMojgArbbYjPF5Bh_81ozQPt8D7Ffrt2hXnlCQJ4Cim60djDVootTmixI1cDEKjIFQ7gZEluRQRz6yXUJU2F7tfsAsM2iJaTs-vCovMChWl9QKqINYmtMAh1qzrdlSFPVycRIm_fwI5xZWnmxGwi5r3cLqXzVxOyLLvAFet9-sRdxKd2YmnLZQPbG4N8J6muT7MKiTebMwDer6utxPaUMjGOMZHXSBa_6Kti0a8d3Ws2QTzZhIqNFFjbb7uHHp65jnsACD6KRJM4TdQUntJENLF5w5IiCENS1Q41DesxspZwU8eZYllWzYicm4QwS8U2ECeITrrfLIdQY3eDknvsAXeCYwbAAAAAFsnDtiAA"

# Custom Animated Emojis Mapping
PREMIUM_EMOJI_IDS = {
    "✅": "5444987348334965906", "❌": "5447647474984449520", "🔥": "5116414868357907335",
    "⚡": "5219943216781995020", "💳": "5447453226498552490", "💠": "4904936030232117798",
    "📝": "6266764202950530136", "🌐": "5447602197439218445", "📊": "5445146408153806223",
    "📦": "5303102515301083665", "📋": "4904936030232117798", "⏳": "5258113901106580375",
    "🚀": "5343887395894882351", "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738", "📈": "5134457377428341766",
    "🔢": "5444931419270839381", "🔌": "5120722716260828125", "⭐️": "5172716095697584957",
    "🆓": "5406756500108501710", "👑": "6266995104687330978", "🔍": "5258396243666681152",
    "⏱️": "5343927661213279013", "💥": "5122933683820430249", "🆔": "5447311106030726740",
    "👤": "5445174334031166029", "📅": "5343927661213279013", "🔄": "5454245266305604993",
    "🏦": "5445408306669582934", "🥰": "5444931419270839381", "😱": "5447181973544008180",
    "🔷": "5301275719681190738", "🔑": "5454386656628991407", "📆": "5343927661213279013",
    "👥": "5454371323595744068", "🥕": "5447653032672129347", "➡️": "5445350109862720603",
    "🦉": "5123344136665039833", "🍑": "5445408306669582934", "💪": "5305622454218024328",
    "🌝": "5341684837881235158", "📁": "5444908424015934570", "ℹ️": "5289930378885214069",
    "💀": "5231338559587257737", "📢": "5116445341150872576", "💰": "5116648080787112958",
    "🔘": "5219901967916084166", "🔗": "5447479640547428304", "👇": "5122933683820430249",
    "📌": "5447187153274567373", "🍳": "5305622454218024328", "💸": "5283232570660634549",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958", "🚫": "5116151848855667552",
    "🛒": "5447319442562251569", "🔧": "4904936030232117798", "⛔️": "5275969776668134187",
    "🥲": "4904468402782864209", "☠️": "5231338559587257737", "🛡": "5219672809936006424",
    "📸": "5445344161333015312", "💬": "5447510826304959724", "😺": "5118590136149345664",
    "🌍": "5303440357428586778", "🔹": "5301275719681190738", "📹": "5445158077579952110",
    "📡": "5447448489149625830", "🌟": "5310224206732996002", "📍": "5447187153274567373",
    "🔐": "5258476306152038031", "😇": "6321225560789877992", "👌": "5445350109862720603",
    "⭐": "6267298050205553492", "🍭": "6267152480878990865", "⚙️": "5258023599419171861",
    "⛔": "4918014360267260850", "📥": "5350747347724810871", "💵": "5350711759625795085",
    "️🏷️": "5436285465420383204", "📂": "5444908424015934570", "🛠️": "5348239232852836489",
    "📄️": "5323538339062628165", "📎": "5282531402821991529", "🖥️": "5258574977633567931",
    "⌨️": "5258334330740171131", "🛡️": "5219672809936006424", "🔒": "5258476306152038031",
    "🔓": "5258476306152038031", "📤": "5350747347724810871", "🕒": "5258113901106580375",
}

def premium_emoji(text: str) -> str:
    if not text:
        return text
    result = text
    for emoji, emoji_id in PREMIUM_EMOJI_IDS.items():
        result = result.replace(emoji, f'<emoji id="{emoji_id}">{emoji}</emoji>')
    return result

# Add all your GIF/Video message IDs here!
START_MEDIA_IDS = [2, 3, 4, 5, 6, 7, 9, 10]
CURRENT_MEDIA_INDEX = 0

# Initialize both the Bot (for talking) and the Userbot (for scraping)
bot = Client("scraper_bot_interface", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("scraper_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# ==================== MESSAGES ====================
WELCOME_MESSAGE = premium_emoji(
    "👋 <b>𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 𝗙𝗥𝗢𝗫𝗧 𝗦𝗰𝗿𝗮𝗽𝗲𝗿 𝗕𝗼𝘁!</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "<i>System Status:</i> <b>ONLINE</b> 🟢\n"
    "<i>Clearance:</i> <b>VERIFIED</b> 🛡️\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "I am ready to extract targets with deadly precision.\n"
    "Access the <b>Cmds</b> panel below to begin operations."
)

HELP_MESSAGE = premium_emoji(
    "📋 <b>𝗙𝗥𝗢𝗫𝗧 𝗠𝗢𝗗𝗨𝗟𝗘 𝗦𝗘𝗟𝗘𝗖𝗧𝗜𝗢𝗡</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Select an operational module below to view its advanced parameters and execution protocols."
)

SCRAPER_INFO = premium_emoji(
    "🕷️ <b>𝗠𝗢𝗗𝗨𝗟𝗘: 𝗦𝗖𝗥𝗔𝗣𝗘𝗥 (/scr or /copy)</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Extract targeted data from any network with deadly precision.\n\n"
    "<b>[ EXECUTION PROTOCOLS ]</b>\n"
    "➥ <code>/scr https://t.me/group 1000 keyword</code>\n"
    "<i>(Extracts from the last 1000 messages)</i>\n\n"
    "➥ <code>/scr https://t.me/group all keyword</code>\n"
    "<i>(Extracts entire history)</i>\n\n"
    "➥ <code>/scr https://t.me/group 01/02 to 05/06 keyword</code>\n"
    "<i>(Extracts strictly between DD/MM dates)</i>"
)

SPLIT_INFO = premium_emoji(
    "✂️ <b>𝗠𝗢𝗗𝗨𝗟𝗘: 𝗦𝗣𝗟𝗜𝗧 (/split)</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Slice massive data dumps into perfectly sized deployment chunks.\n\n"
    "<b>[ EXECUTION PROTOCOLS ]</b>\n"
    "➡️ Wait for the system to drop a scraped <code>.txt</code> file.\n"
    "➡️ <b>Reply</b> directly to that file in the chat.\n"
    "➡️ Transmit command: <code>/split 50</code> (or any integer).\n\n"
    "<i>The system will instantly partition the file and upload the chunks back to you.</i>"
)

CLEAN_INFO = premium_emoji(
    "🧹 <b>𝗠𝗢𝗗𝗨𝗟𝗘: 𝗖𝗟𝗘𝗔𝗡 (/clean)</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Remove expired and duplicate cards from your files.\n\n"
    "<b>[ EXECUTION PROTOCOLS ]</b>\n"
    "➡️ Reply to a card file <code>.txt</code> with <code>/clean</code>.\n"
    "➡️ The system will check all cards for expiration.\n"
    "➡️ Current month/year is used to validate cards.\n"
    "➡️ Duplicate cards are automatically removed.\n\n"
    "<i>The system will return a clean file with only valid, unique cards.</i>"
)

CHECK_INFO = premium_emoji(
    "🔎 <b>𝗠𝗢𝗗𝗨𝗟𝗘: 𝗖𝗛𝗘𝗖𝗞 (/check)</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "Analyze cards and separate Private from Public.\n\n"
    "<b>[ EXECUTION PROTOCOLS ]</b>\n"
    "➡️ Reply to a card file <code>.txt</code> with <code>/check</code>.\n"
    "➡️ The system will analyze all cards in the file.\n"
    "➡️ Private cards are identified by BIN range.\n"
    "➡️ Public cards are identified by BIN range.\n\n"
    "<i>The system will return:\n"
    "- Total cards count\n"
    "- Private cards count & percentage\n"
    "- Public cards count & percentage\n"
    "- Private cards file\n"
    "- Public cards file</i>"
)

# ==================== KEYBOARDS ====================
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="𝙲𝙷𝙰𝙽𝙽𝙴𝙻", url="https://t.me/+ed0DHD3KZ4I0ZWU1", style="primary"),
                InlineKeyboardButton(text="𝙲𝙼𝙳𝚂", callback_data="show_cmds", style="primary")
            ],
            [
                InlineKeyboardButton(text="𝙰𝙳𝙼𝙸𝙽", url="https://t.me/FROXT_07", style="primary")
            ],
            [
                InlineKeyboardButton(text="ᴄʟᴏꜱᴇ", callback_data="exit_bot", style="danger")
            ]
        ]
    )

def get_cmds_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="𝚂𝚌𝚛𝚊𝚙𝚎", callback_data="cmd_scraper", style="primary"),
                InlineKeyboardButton(text="𝚂𝚙𝚕𝚒𝚝", callback_data="cmd_split", style="primary")
            ],
            [
                InlineKeyboardButton(text="𝙲𝚕𝚎𝚊𝚗", callback_data="cmd_clean", style="primary"),
                InlineKeyboardButton(text="𝙲𝚑𝚎𝚌𝚔", callback_data="cmd_check", style="primary")
            ],
            [
                InlineKeyboardButton(text="Bᴀᴄᴋ", callback_data="back_start", style="danger")
            ]
        ]
    )

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Bᴀᴄᴋ", callback_data="show_cmds")]
        ]
    )

@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    global CURRENT_MEDIA_INDEX
    
    # Get current media ID and increment the index for the next person
    media_id = START_MEDIA_IDS[CURRENT_MEDIA_INDEX]
    CURRENT_MEDIA_INDEX = (CURRENT_MEDIA_INDEX + 1) % len(START_MEDIA_IDS)

    try:
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id="@froxtassets",
            message_id=media_id,
            caption=WELCOME_MESSAGE,
            reply_markup=get_main_menu_keyboard(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        # Fallback if fetching from channel fails
        await message.reply_text(WELCOME_MESSAGE, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.HTML)


@bot.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    if query.data == "show_cmds":
        try:
            await query.message.edit_caption(
                caption=HELP_MESSAGE,
                reply_markup=get_cmds_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except:
            await query.message.edit_text(
                text=HELP_MESSAGE,
                reply_markup=get_cmds_keyboard(),
                parse_mode=ParseMode.HTML
            )
            
    elif query.data == "cmd_scraper":
        try:
            await query.message.edit_caption(
                caption=SCRAPER_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except:
            await query.message.edit_text(
                text=SCRAPER_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
            
    elif query.data == "cmd_split":
        try:
            await query.message.edit_caption(
                caption=SPLIT_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except:
            await query.message.edit_text(
                text=SPLIT_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
            
    elif query.data == "cmd_clean":
        try:
            await query.message.edit_caption(
                caption=CLEAN_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except:
            await query.message.edit_text(
                text=CLEAN_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
            
    elif query.data == "cmd_check":
        try:
            await query.message.edit_caption(
                caption=CHECK_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except:
            await query.message.edit_text(
                text=CHECK_INFO,
                reply_markup=get_back_keyboard(),
                parse_mode=ParseMode.HTML
            )
            
    elif query.data == "back_start":
        try:
            await query.message.edit_caption(
                caption=WELCOME_MESSAGE,
                reply_markup=get_main_menu_keyboard(),
                parse_mode=ParseMode.HTML
            )
        except:
            await query.message.edit_text(
                text=WELCOME_MESSAGE,
                reply_markup=get_main_menu_keyboard(),
                parse_mode=ParseMode.HTML
            )
            
    elif query.data == "exit_bot":
        exit_text = premium_emoji(
            "☠️ <b>𝗦𝗘𝗦𝗦𝗜𝗢𝗡 𝗧𝗘𝗥𝗠𝗜𝗡𝗔𝗧𝗘𝗗</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "<i>Thank you for using FROXT Scraper.</i>\n"
            "<i>System entering sleep mode...</i> 💤"
        )
        try:
            await query.message.delete()
            await client.send_message(query.message.chat.id, exit_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Failed to delete message: {e}")

# ==================== COMMANDS ====================

@bot.on_message(filters.command(["copy", "scr"]))
async def copy_command(client: Client, message: Message):
    try:
        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            await message.reply_text("❌ **Invalid Format.**\nExample: `/copy https://t.me/group 100 keyword`")
            return

        command = args[0]
        group_link = args[1]
        limit_or_date = args[2]
        keyword = args[3]

        # Handle joining if it's a private link
        chat_id = group_link
        if "joinchat" in group_link or "+" in group_link:
            try:
                chat = await userbot.join_chat(group_link)
                chat_id = chat.id
            except Exception as e:
                pass # Already in chat or invalid
        else:
            chat_id = group_link.replace("https://t.me/", "@")

        # Parse limit / dates
        limit = 0
        date_range = False
        start_date = None
        end_date = None

        if limit_or_date.lower() == "all":
            limit = 0
        elif "to" in limit_or_date.lower():
            date_range = True
            dates = limit_or_date.lower().split("to")
            try:
                current_year = datetime.now().year
                start_date = datetime.strptime(f"{dates[0].strip()}/{current_year}", "%d/%m/%Y")
                end_date = datetime.strptime(f"{dates[1].strip()}/{current_year}", "%d/%m/%Y")
            except ValueError:
                await message.reply_text("❌ Invalid date format. Use DD/MM to DD/MM")
                return
        else:
            try:
                limit = int(limit_or_date)
            except ValueError:
                await message.reply_text("❌ Limit must be a number, 'all', or a date range.")
                return

        status_msg = await message.reply_text(f"⏳ <b>Initializing Deep Scrape...</b>\nTarget: <code>{group_link}</code>", parse_mode=ParseMode.HTML)

        found_lines = []
        scraped_count = 0
        start_time = time.time()
        last_update_time = time.time()

        # Use search_messages for quick limited searches, but get_chat_history for ALL to bypass Telegram's 10,000 search limit
        if limit > 0:
            message_iterator = userbot.search_messages(chat_id=chat_id, query=keyword, limit=limit)
        else:
            message_iterator = userbot.get_chat_history(chat_id=chat_id)

        async for msg in message_iterator:
            scraped_count += 1
            
            if date_range and msg.date:
                # Check date boundaries
                if not (start_date <= msg.date <= end_date):
                    continue

            if msg.text:
                # If using get_chat_history, we must strictly check if the message even contains the keyword first
                if limit == 0 and keyword.lower() not in msg.text.lower():
                    pass
                else:
                    for line in msg.text.split('\n'):
                        if keyword.lower() in line.lower():
                            # Remove the keyword completely, then remove dot/space and colon
                            new_line = re.sub(re.escape(keyword), "", line, flags=re.IGNORECASE)
                            new_line = new_line.replace(". ", "").replace(".", "").strip()
                            found_lines.append(new_line)
                        
            # Update the status message every 1.5 seconds to show a "live" counting effect without hitting rate limits
            current_time = time.time()
            if current_time - last_update_time > 1.5:
                try:
                    await status_msg.edit_text(
                        f"⏳ <b>𝗘𝗫𝗧𝗥𝗔𝗖𝗧𝗜𝗡𝗚 𝗗𝗔𝗧𝗔</b>\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"📡 <b>Scanning:</b> <code>{scraped_count}</code> messages\n"
                        f"🎯 <b>Matches:</b> <code>{len(found_lines)}</code> lines\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"<i>Deep Scan in progress...</i>",
                        parse_mode=ParseMode.HTML
                    )
                    last_update_time = current_time
                except:
                    pass
        
        elapsed_time = round(time.time() - start_time, 2)
        
        if not found_lines:
            await status_msg.edit_text(f"❌ No lines found containing '{keyword}'.\nChecked {scraped_count} messages in {elapsed_time}s.")
            return
            
        # Create a text file
        file_name = f"scraped_{int(time.time())}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            for line in found_lines[::-1]:
                f.write(line + "\n")
                
        # Send the file via the BOT
        caption = premium_emoji(
            f"💎 <b>𝗙𝗥𝗢𝗫𝗧 𝗦𝗖𝗥𝗔𝗣𝗘𝗥 𝗥𝗘𝗦𝗨𝗟𝗧𝗦</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 <b>Keyword</b> ➾ <code>{keyword}</code>\n"
            f"📢 <b>Source</b> ➾ <code>{group_link}</code>\n"
            f"⚡ <b>Total Scraped</b> ➾ <code>{scraped_count}</code>\n"
            f"✅ <b>Lines Found</b> ➾ <code>{len(found_lines)}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 <b>Checked By</b> ➾ @FROXT_07"
        )
        await message.reply_document(document=file_name, caption=caption, parse_mode=ParseMode.HTML)
        
        # Cleanup
        os.remove(file_name)

    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {e}")

@bot.on_message(filters.command("split"))
async def split_command(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text("❌ Please reply to a scraped .txt file with this command.")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("❌ Please specify a number, e.g., `/split 50`")
            return
            
        chunk_size = int(args[1])
        if chunk_size <= 0:
            await message.reply_text("❌ Number must be greater than 0.")
            return

        status_msg = await message.reply_text("⏳ Downloading file...")
        
        # Download the file
        file_path = await message.reply_to_message.download()
        
        if not file_path:
            await status_msg.edit_text("❌ Failed to download the file.")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        os.remove(file_path)
        
        if not lines:
            await status_msg.edit_text("❌ The file is empty.")
            return

        total_lines = len(lines)
        if chunk_size >= total_lines:
            await status_msg.edit_text(f"❌ The file only has {total_lines} lines. No need to split by {chunk_size}!")
            return

        await status_msg.edit_text("⏳ Splitting file...")
        
        # Split into chunks
        chunks = [lines[i:i + chunk_size] for i in range(0, total_lines, chunk_size)]
        
        # Save chunks and send them
        for idx, chunk in enumerate(chunks, 1):
            chunk_file_name = f"part_{idx}_{int(time.time())}.txt"
            with open(chunk_file_name, "w", encoding="utf-8") as f:
                f.writelines(chunk)
                
            await message.reply_document(
                document=chunk_file_name,
                caption=f"✅ **Part {idx}**\nLines: {len(chunk)}"
            )
            os.remove(chunk_file_name)
            
        await status_msg.edit_text(f"✅ Successfully split into {len(chunks)} files!")
        
    except ValueError:
        await message.reply_text("❌ Please provide a valid number. Example: `/split 50`")
    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {e}")

@bot.on_message(filters.command("mc"))
async def mc_command(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 4:
            await message.reply_text("❌ **Invalid Format.**\nExample: `/mc https://t.me/grp1 https://t.me/grp2 100 keyword`")
            return

        command = args[0]
        keyword = args[-1]
        limit_or_date = args[-2]
        group_links = args[1:-2]

        limit = 0
        date_range = False
        start_date = None
        end_date = None

        if limit_or_date.lower() == "all":
            limit = 0
        elif "to" in limit_or_date.lower():
            date_range = True
            dates = limit_or_date.lower().split("to")
            try:
                current_year = datetime.now().year
                start_date = datetime.strptime(f"{dates[0].strip()}/{current_year}", "%d/%m/%Y")
                end_date = datetime.strptime(f"{dates[1].strip()}/{current_year}", "%d/%m/%Y")
            except ValueError:
                await message.reply_text("❌ Invalid date format. Use DD/MM to DD/MM")
                return
        else:
            try:
                limit = int(limit_or_date)
            except ValueError:
                await message.reply_text("❌ Limit must be a number, 'all', or a date range.")
                return

        status_msg = await message.reply_text(premium_emoji(f"⏳ <b>Initializing Multi-Scrape...</b>"), parse_mode=ParseMode.HTML)

        all_found_lines = []
        total_scraped_count = 0
        start_time = time.time()

        for group_link in group_links:
            await status_msg.edit_text(premium_emoji(f"⏳ <b>Scanning:</b> <code>{group_link}</code>..."), parse_mode=ParseMode.HTML)
            chat_id = group_link
            if "joinchat" in group_link or "+" in group_link:
                try:
                    chat = await userbot.join_chat(group_link)
                    chat_id = chat.id
                except:
                    pass
            else:
                chat_id = group_link.replace("https://t.me/", "@")

            try:
                if limit > 0:
                    message_iterator = userbot.search_messages(chat_id=chat_id, query=keyword, limit=limit)
                else:
                    message_iterator = userbot.get_chat_history(chat_id=chat_id)

                async for msg in message_iterator:
                    total_scraped_count += 1
                    if date_range and msg.date:
                        if not (start_date <= msg.date <= end_date):
                            continue
                    if msg.text:
                        if limit == 0 and keyword.lower() not in msg.text.lower():
                            pass
                        else:
                            for line in msg.text.split('\n'):
                                if keyword.lower() in line.lower():
                                    new_line = re.sub(re.escape(keyword), "", line, flags=re.IGNORECASE)
                                    new_line = new_line.replace(". ", "").replace(".", "").strip()
                                    all_found_lines.append(new_line)
            except Exception as e:
                print(f"Error scraping {group_link}: {e}")

        unique_lines = list(set(all_found_lines))
        duplicates = len(all_found_lines) - len(unique_lines)
        
        if not unique_lines:
            await status_msg.edit_text(premium_emoji(f"❌ <b>No lines found containing '{keyword}'.</b>"))
            return
            
        file_name = f"scraped_mc_{int(time.time())}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            for line in unique_lines[::-1]:
                f.write(line + "\n")
                
        caption = premium_emoji(
            f"💎 <b>𝗙𝗥𝗢𝗫𝗧 𝗠𝗨𝗟𝗧𝗜-𝗦𝗖𝗥𝗔𝗣𝗘𝗥</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 <b>Keyword</b> ➾ <code>{keyword}</code>\n"
            f"📢 <b>Sources</b> ➾ <code>{len(group_links)} Channels</code>\n"
            f"⚡ <b>Total Scraped</b> ➾ <code>{total_scraped_count}</code>\n"
            f"✅ <b>Unique Found</b> ➾ <code>{len(unique_lines)}</code>\n"
            f"🗑️ <b>Duplicates Removed</b> ➾ <code>{duplicates}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 <b>Checked By</b> ➾ @FROXT_07"
        )
        await message.reply_document(document=file_name, caption=caption, parse_mode=ParseMode.HTML)
        os.remove(file_name)
        await status_msg.delete()

    except Exception as e:
        print(f"Error in mc_command: {e}")


@bot.on_message(filters.command("scall"))
async def scall_command(client: Client, message: Message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply_text("❌ **Invalid Format.**\nExample: `/scall 100 keyword`")
            return

        command = args[0]
        limit_or_date = args[1]
        keyword = args[2]

        limit = 0
        date_range = False
        start_date = None
        end_date = None

        if limit_or_date.lower() == "all":
            limit = 0
        elif "to" in limit_or_date.lower():
            date_range = True
            dates = limit_or_date.lower().split("to")
            try:
                current_year = datetime.now().year
                start_date = datetime.strptime(f"{dates[0].strip()}/{current_year}", "%d/%m/%Y")
                end_date = datetime.strptime(f"{dates[1].strip()}/{current_year}", "%d/%m/%Y")
            except ValueError:
                await message.reply_text("❌ Invalid date format. Use DD/MM to DD/MM")
                return
        else:
            try:
                limit = int(limit_or_date)
            except ValueError:
                await message.reply_text("❌ Limit must be a number, 'all', or a date range.")
                return

        status_msg = await message.reply_text(premium_emoji(f"⏳ <b>Gathering Joined Channels...</b>"), parse_mode=ParseMode.HTML)

        channels = []
        async for dialog in userbot.get_dialogs():
            if dialog.chat and dialog.chat.type in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
                channels.append(dialog.chat)

        if not channels:
            await status_msg.edit_text(premium_emoji("❌ <b>No channels found!</b>"))
            return

        await status_msg.edit_text(premium_emoji(f"📊 <b>Found {len(channels)} channels. Starting scrape...</b>"), parse_mode=ParseMode.HTML)

        all_found_lines = []
        total_scraped_count = 0
        processed = 0

        for chat in channels:
            processed += 1
            await status_msg.edit_text(premium_emoji(f"⏳ <b>Scraping {processed}/{len(channels)}</b>\n📁 <code>{chat.title}</code>"), parse_mode=ParseMode.HTML)
            try:
                if limit > 0:
                    message_iterator = userbot.search_messages(chat_id=chat.id, query=keyword, limit=limit)
                else:
                    message_iterator = userbot.get_chat_history(chat_id=chat.id)

                async for msg in message_iterator:
                    total_scraped_count += 1
                    if date_range and msg.date:
                        if not (start_date <= msg.date <= end_date):
                            continue
                    if msg.text:
                        if limit == 0 and keyword.lower() not in msg.text.lower():
                            pass
                        else:
                            for line in msg.text.split('\n'):
                                if keyword.lower() in line.lower():
                                    new_line = re.sub(re.escape(keyword), "", line, flags=re.IGNORECASE)
                                    new_line = new_line.replace(". ", "").replace(".", "").strip()
                                    all_found_lines.append(new_line)
            except Exception as e:
                pass

        unique_lines = list(set(all_found_lines))
        duplicates = len(all_found_lines) - len(unique_lines)
        
        if not unique_lines:
            await status_msg.edit_text(premium_emoji(f"❌ <b>No lines found in any channel.</b>"))
            return
            
        file_name = f"scraped_scall_{int(time.time())}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            for line in unique_lines[::-1]:
                f.write(line + "\n")
                
        caption = premium_emoji(
            f"💎 <b>𝗙𝗥𝗢𝗫𝗧 𝗚𝗟𝗢𝗕𝗔𝗟 𝗦𝗖𝗥𝗔𝗣𝗘𝗥</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 <b>Keyword</b> ➾ <code>{keyword}</code>\n"
            f"📢 <b>Sources</b> ➾ <code>All Channels ({len(channels)})</code>\n"
            f"⚡ <b>Total Scraped</b> ➾ <code>{total_scraped_count}</code>\n"
            f"✅ <b>Unique Found</b> ➾ <code>{len(unique_lines)}</code>\n"
            f"🗑️ <b>Duplicates Removed</b> ➾ <code>{duplicates}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👨‍💻 <b>Checked By</b> ➾ @FROXT_07"
        )
        await message.reply_document(document=file_name, caption=caption, parse_mode=ParseMode.HTML)
        os.remove(file_name)
        await status_msg.delete()

    except Exception as e:
        print(f"Error in scall_command: {e}")

# ==================== CLEAN COMMAND ====================
@bot.on_message(filters.command("clean"))
async def clean_command(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text(premium_emoji("❌ Please reply to a card <code>.txt</code> file with this command."))
        return

    status_msg = await message.reply_text(premium_emoji("⏳ <b>Downloading file...</b>"))
    
    try:
        file_path = await message.reply_to_message.download()
        
        if not file_path:
            await status_msg.edit_text(premium_emoji("❌ Failed to download file"))
            return
            
        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        os.remove(file_path)
        
        if not lines:
            await status_msg.edit_text(premium_emoji("❌ File is empty"))
            return
            
        lines = [line.strip() for line in lines if line.strip()]
        current_year = datetime.now().year % 100
        current_month = datetime.now().month
        
        valid_cards = []
        seen_cards = set()
        expired_count = 0
        duplicate_count = 0
        
        for line in lines:
            parts = line.split('|')
            if len(parts) >= 4:
                try:
                    card_month = int(parts[1].strip())
                    card_year = int(parts[2].strip())
                    card_number = parts[0].strip()
                    
                    if card_year < current_year or (card_year == current_year and card_month < current_month):
                        expired_count += 1
                        continue
                        
                    if card_number in seen_cards:
                        duplicate_count += 1
                        continue
                        
                    seen_cards.add(card_number)
                    valid_cards.append(line)
                except (ValueError, IndexError):
                    if line in seen_cards:
                        duplicate_count += 1
                        continue
                    seen_cards.add(line)
                    valid_cards.append(line)
            else:
                if line in seen_cards:
                    duplicate_count += 1
                    continue
                seen_cards.add(line)
                valid_cards.append(line)
        
        if not valid_cards:
            await status_msg.edit_text(
                premium_emoji(
                    f"❌ <b>No valid cards found!</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🗑️ Expired: {expired_count:,}\n"
                    f"🔄 Duplicates: {duplicate_count:,}"
                )
            )
            return
            
        output_file = f"cleaned_{int(time.time())}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(valid_cards))
            
        caption = premium_emoji(
            f"🧹 <b>𝗖𝗟𝗘𝗔𝗡𝗘𝗗 𝗖𝗔𝗥𝗗𝗦</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ <b>Valid Cards</b> ➾ <code>{len(valid_cards):,}</code>\n"
            f"🗑️ <b>Expired Removed</b> ➾ <code>{expired_count:,}</code>\n"
            f"🔄 <b>Duplicates Removed</b> ➾ <code>{duplicate_count:,}</code>\n"
            f"📊 <b>Total Removed</b> ➾ <code>{expired_count + duplicate_count:,}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>Checked Against:</b> {datetime.now().strftime('%B %Y')}"
        )
        
        await message.reply_document(document=output_file, caption=caption, parse_mode=ParseMode.HTML)
        os.remove(output_file)
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(premium_emoji(f"❌ Error: {str(e)}"))
        if 'file_path' in locals() and file_path and os.path.exists(file_path):
            os.remove(file_path)

# ==================== CHECK COMMAND ====================
@bot.on_message(filters.command("check"))
async def check_command(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text(premium_emoji("❌ Please reply to a card <code>.txt</code> file with this command."))
        return

    status_msg = await message.reply_text(premium_emoji("⏳ <b>Processing file...</b>"))
    
    try:
        file_path = await message.reply_to_message.download()
        
        if not file_path:
            await status_msg.edit_text(premium_emoji("❌ Failed to download file"))
            return
            
        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        os.remove(file_path)
        
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            await status_msg.edit_text(premium_emoji("❌ File is empty"))
            return
            
        private_cards = []
        public_cards = []
        
        for line in lines:
            parts = line.split('|')
            if parts:
                card_number = parts[0].strip()
                if card_number and card_number[0].isdigit():
                    first_digit = card_number[0]
                    if first_digit in ['4', '5', '6', '3', '2']:
                        private_cards.append(line)
                    else:
                        public_cards.append(line)
                else:
                    public_cards.append(line)
            else:
                public_cards.append(line)
        
        total = len(private_cards) + len(public_cards)
        private_count = len(private_cards)
        private_percentage = (private_count / total * 100) if total > 0 else 0
        public_count = total - private_count
        public_percentage = 100 - private_percentage
        
        if total == 0:
            await status_msg.edit_text(premium_emoji("❌ No valid cards found in the file."))
            return
            
        result_text = premium_emoji(
            f"🔎 <b>𝗖𝗛𝗘𝗖𝗞 𝗥𝗘𝗦𝗨𝗟𝗧𝗦</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📊 <b>Total Cards:</b> <code>{total:,}</code>\n"
            f"🔒 <b>Private:</b> <code>{private_count:,}</code>\n"
            f"🌐 <b>Public:</b> <code>{public_count:,}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📈 <b>Private Percentage:</b> <code>{private_percentage:.2f}%</code>\n"
            f"📉 <b>Public Percentage:</b> <code>{public_percentage:.2f}%</code>"
        )
        
        await status_msg.edit_text(result_text)
        
        # Send private cards
        if private_cards:
            private_file = f"private_{int(time.time())}.txt"
            with open(private_file, "w", encoding="utf-8") as f:
                f.write("\n".join(private_cards))
            await message.reply_document(
                document=private_file,
                caption=premium_emoji(f"🔒 <b>Private Cards</b>\nCount: <code>{len(private_cards):,}</code>")
            )
            os.remove(private_file)
        
        # Send public cards
        if public_cards:
            public_file = f"public_{int(time.time())}.txt"
            with open(public_file, "w", encoding="utf-8") as f:
                f.write("\n".join(public_cards))
            await message.reply_document(
                document=public_file,
                caption=premium_emoji(f"🌐 <b>Public Cards</b>\nCount: <code>{len(public_cards):,}</code>")
            )
            os.remove(public_file)
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(premium_emoji(f"❌ Error: {str(e)}"))
        if 'file_path' in locals() and file_path and os.path.exists(file_path):
            os.remove(file_path)


async def main():
    print("Starting Bot Interface...")
    await bot.start()
    
    print("Starting Background Userbot...")
    await userbot.start()
    
    try:
        print("Populating Userbot peer database...")
        async for _ in userbot.get_dialogs(limit=100):
            pass
    except:
        pass
        
    print("FROXT Scraper is fully online and ready!")
    await idle()
    
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    bot.run(main())
