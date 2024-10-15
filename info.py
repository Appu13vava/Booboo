import re
from os import environ
from pyrogram import Client, filters, errors

id_pattern = re.compile(r'^-?\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
BOT_TOKEN = environ['BOT_TOKEN']

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', False))
PICS = (environ.get('PICS', 'https://telegra.ph/file/7e56d907542396289fee4.jpg https://telegra.ph/file/9aa8dd372f4739fe02d85.jpg')).split()

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '5788022702').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1002419514074').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL', '-1002274050803')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "your_database_uri")
DATABASE_NAME = environ.get('DATABASE_NAME', "appu")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002243715608'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'TeamEvamaria')
P_TTI_SHOW_OFF = is_enabled(environ.get('P_TTI_SHOW_OFF', "False"), False)
IMDB = is_enabled(environ.get('IMDB', "True"), True)
SINGLE_BUTTON = is_enabled(environ.get('SINGLE_BUTTON', "False"), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", None)
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "<b>Query: {query}</b> ...")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled(environ.get('MELCOW_NEW_USERS', "True"), True)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT', "False"), False)
PUBLIC_FILE_STORE = is_enabled(environ.get('PUBLIC_FILE_STORE', "True"), True)

# Initialize the bot
app = Client(SESSION, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.chat(AUTH_CHANNEL) & filters.new_chat_members)
async def welcome_new_user(client, message):
    for new_member in message.new_chat_members:
        try:
            # Send a welcome message and inform them they need to join the channel
            await message.chat.send_message(
                new_member.id,
                f"Welcome {new_member.mention}! Please ensure you are subscribed to the channel {AUTH_CHANNEL} to use this bot."
            )
        except errors.FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception as e:
            print(f"Error sending message to {new_member.id}: {e}")

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    
    # Check if the user is subscribed
    is_subscribed = await check_user_subscription(client, user_id)
    
    if is_subscribed:
        await message.reply("Welcome! You're subscribed.")
    else:
        await message.reply(f"Please subscribe to the channel to use this bot. You can join here: https://t.me/{AUTH_CHANNEL}")

async def check_user_subscription(bot, user_id):
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, user_id)
        return user.status in ["member", "administrator"]
    except errors.UserNotParticipant:
        print("User is not subscribed to the channel.")
        return False
    except errors.ChatAdminRequired:
        print("Bot requires admin rights to access the channel.")
        return False
    except KeyError:
        print("Peer ID not found in cache.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    app.run()
