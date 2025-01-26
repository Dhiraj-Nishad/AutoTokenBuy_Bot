import re
from telethon import TelegramClient, events

# Replace these with your credentials
API_ID = 29199461
API_HASH = '5d5c0797293505649aaa30aa8d1af14a'
SESSION_NAME = 'auto_buy_session'

# List of source group IDs
SOURCE_GROUP_IDS = ['@buybotttttt', '@buybottttt']  # Add more groups as needed
TROJAN_BOT_ID = '@bonkbot_bot'

SOLANA_ADDRESS_REGEX = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Event listener for new messages in the source groups
@client.on(events.NewMessage(chats=SOURCE_GROUP_IDS))
async def forward_to_trojan(event):
    try:
        message_text = event.message.message
        sol_addresses = re.findall(SOLANA_ADDRESS_REGEX, message_text)

        if sol_addresses:
            for address in sol_addresses:
                await client.send_message(TROJAN_BOT_ID, address)
                print(f"Forwarded Solana address to Trojan Bot: {address}")
        else:
            print("No valid Solana address found in the message.")
    except Exception as e:
        print(f"Error occurred: {e}")

def main():
    print("Starting the Telegram client...")
    with client:
        print("Listening for new messages...")
        client.run_until_disconnected()

if __name__ == "__main__":
    main()
