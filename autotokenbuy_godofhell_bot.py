import re
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, filters
from telethon import TelegramClient

# Replace these with your credentials
API_ID = API_ID = 29199461  # Get this from https://my.telegram.org   # Get this from https://my.telegram.org
API_HASH = '5d5c0797293505649aaa30aa8d1af14a'  # Get this from https://my.telegram.org
BOT_TOKEN = '8180740607:AAFxS6mFw8tZyhItsfamQyl8iJc9NWp3kvU'  # Get this from BotFather

# Solana address regex pattern (matches valid Solana token contract addresses)
SOLANA_ADDRESS_REGEX = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'

# Initialize Telethon client for monitoring groups
telethon_client = TelegramClient('bot_session', API_ID, API_HASH)

# Initialize Telegram bot
bot = Bot(token=BOT_TOKEN)

# Global variables to store source and target group IDs
source_group_id = None  # Initially unset
target_group_id = None  # Initially unset

# Command: /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Telegram Bot. If you are facing any issues, contact me @godofhelll.\n\n"
        "Use the following commands to configure the bot:\n"
        "/setsource <group_id> - Set the source group ID\n"
        "/settarget <group_id> - Set the target group ID\n"
        "/status - Check current configuration"
    )

# Command: /setsource <group_id>
def set_source(update: Update, context: CallbackContext):
    global source_group_id
    try:
        source_group_id = int(context.args[0])  # Get group ID from command arguments
        
        # Fetch group details using Bot API
        chat = bot.get_chat(source_group_id)
        source_group_name = chat.title

        update.message.reply_text(f"Source group added successfully.\nGroup Name: {source_group_name}")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /setsource <group_id>")
    except Exception as e:
        update.message.reply_text(f"Error adding source group: {e}")

# Command: /settarget <group_id>
def set_target(update: Update, context: CallbackContext):
    global target_group_id
    try:
        target_group_id = int(context.args[0])  # Get group ID from command arguments
        
        # Fetch group details using Bot API
        chat = bot.get_chat(target_group_id)
        target_group_name = chat.title

        update.message.reply_text(f"Target group added successfully.\nGroup Name: {target_group_name}")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /settarget <group_id>")
    except Exception as e:
        update.message.reply_text(f"Error adding target group: {e}")

# Command: /status
def status(update: Update, context: CallbackContext):
    global source_group_id, target_group_id

    try:
        # Fetch source and target group names if IDs are set
        source_name = bot.get_chat(source_group_id).title if source_group_id else "Not Set"
        target_name = bot.get_chat(target_group_id).title if target_group_id else "Not Set"

        update.message.reply_text(
            f"Current Configuration:\n"
            f"Source Group ID: {source_group_id or 'Not Set'}\n"
            f"Source Group Name: {source_name}\n"
            f"Target Group ID: {target_group_id or 'Not Set'}\n"
            f"Target Group Name: {target_name}"
        )
    except Exception as e:
        update.message.reply_text(f"Error fetching status: {e}")

# Message handler for Solana contract addresses
def handle_message(update: Update, context: CallbackContext):
    global source_group_id, target_group_id

    if not source_group_id or not target_group_id:
        update.message.reply_text("Source or Target group is not configured. Use /setsource and /settarget.")
        return

    # Check if the message is from the source group
    if update.message.chat.id == source_group_id:
        message_text = update.message.text

        # Extract Solana contract addresses using regex
        sol_addresses = re.findall(SOLANA_ADDRESS_REGEX, message_text)

        if sol_addresses:
            for address in sol_addresses:
                # Forward valid Solana addresses to the target group or bot
                bot.send_message(chat_id=target_group_id, text=address)
                update.message.reply_text(f"Forwarded Solana address to target group: {address}")
        else:
            update.message.reply_text("No valid Solana address found in your message.")

# Main function to start the bot
def main():
    global telethon_client

    # Initialize the Updater and Dispatcher
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers for configuration and status checks
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("setsource", set_source))
    dispatcher.add_handler(CommandHandler("settarget", set_target))
    dispatcher.add_handler(CommandHandler("status", status))

    # Add message handler for processing messages from source group
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling for updates
    print("Bot is running...")
    updater.start_polling()

    # Start Telethon client for monitoring groups (if needed)
    with telethon_client:
        telethon_client.run_until_disconnected()

if __name__ == "__main__":
    main()
