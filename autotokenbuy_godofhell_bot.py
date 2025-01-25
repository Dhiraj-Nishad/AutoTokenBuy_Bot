import re
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telethon import TelegramClient

# Replace these with your credentials
API_ID = 29199461  # Get this from https://my.telegram.org
API_HASH = '5d5c0797293505649aaa30aa8d1af14a'  # Get this from https://my.telegram.org
BOT_TOKEN = '8180740607:AAFxS6mFw8tZyhItsfamQyl8iJc9NWp3kvU'  # Get this from BotFather

# Solana address regex pattern (matches valid Solana token contract addresses)
SOLANA_ADDRESS_REGEX = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'

# Initialize Telethon client for monitoring groups
telethon_client = TelegramClient('bot_session', API_ID, API_HASH)

# Global variables to store source and target group IDs
source_group_id = None  # Initially unset
target_group_id = None  # Initially unset

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Telegram Bot. If you are facing any issues, contact me @godofhelll.\n\n"
        "Use the following commands to configure the bot:\n"
        "/setsource <group_id> - Set the source group ID\n"
        "/settarget <group_id> - Set the target group ID\n"
        "/status - Check current configuration"
    )

# Command: /setsource <group_id>
async def set_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global source_group_id
    try:
        source_group_id = int(context.args[0])  # Get group ID from command arguments
        
        # Fetch group details using Bot API
        chat = await context.bot.get_chat(source_group_id)
        source_group_name = chat.title

        await update.message.reply_text(f"Source group added successfully.\nGroup Name: {source_group_name}")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /setsource <group_id>")
    except Exception as e:
        await update.message.reply_text(f"Error adding source group: {e}")

# Command: /settarget <group_id>
async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global target_group_id
    try:
        target_group_id = int(context.args[0])  # Get group ID from command arguments
        
        # Fetch group details using Bot API
        chat = await context.bot.get_chat(target_group_id)
        target_group_name = chat.title

        await update.message.reply_text(f"Target group added successfully.\nGroup Name: {target_group_name}")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /settarget <group_id>")
    except Exception as e:
        await update.message.reply_text(f"Error adding target group: {e}")

# Command: /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global source_group_id, target_group_id

    try:
        # Fetch source and target group names if IDs are set
        source_name = (await context.bot.get_chat(source_group_id)).title if source_group_id else "Not Set"
        target_name = (await context.bot.get_chat(target_group_id)).title if target_group_id else "Not Set"

        await update.message.reply_text(
            f"Current Configuration:\n"
            f"Source Group ID: {source_group_id or 'Not Set'}\n"
            f"Source Group Name: {source_name}\n"
            f"Target Group ID: {target_group_id or 'Not Set'}\n"
            f"Target Group Name: {target_name}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching status: {e}")

# Message handler for Solana contract addresses
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global source_group_id, target_group_id

    if not source_group_id or not target_group_id:
        await update.message.reply_text("Source or Target group is not configured. Use /setsource and /settarget.")
        return

    # Check if the message is from the source group
    if update.message.chat.id == source_group_id:
        message_text = update.message.text

        # Extract Solana contract addresses using regex
        sol_addresses = re.findall(SOLANA_ADDRESS_REGEX, message_text)

        if sol_addresses:
            for address in sol_addresses:
                # Forward valid Solana addresses to the target group or bot
                await context.bot.send_message(chat_id=target_group_id, text=address)
                await update.message.reply_text(f"Forwarded Solana address to target group: {address}")
        else:
            await update.message.reply_text("No valid Solana address found in your message.")

# Main function to start the bot
def main():
    global telethon_client

    # Initialize the ApplicationBuilder and Dispatcher
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers for configuration and status checks
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setsource", set_source))
    application.add_handler(CommandHandler("settarget", set_target))
    application.add_handler(CommandHandler("status", status))

    # Add message handler for processing messages from source group
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling for updates
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
