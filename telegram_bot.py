import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent_core import AgentCore

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
    print("Error: TELEGRAM_BOT_TOKEN is not set in the .env file.")
    exit(1)

# Initialize Agent
try:
    agent = AgentCore()
except Exception as e:
    print(f"Failed to initialize AgentCore: {e}")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I am your Windows AI Agent. Send me any command to control your computer."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Just type naturally what you want me to do on your Windows machine!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the user message through the Agent ReAct loop."""
    user_message = update.message.text
    
    # Send a typing indicator
    await update.message.chat.send_action(action="typing")
    
    # We use a wrapper to run the blocking agent logic in a thread
    def run_agent():
        # Bypass approval since Telegram is considered a trusted admin interface
        return agent.process_message(user_message, bypass_approval=True)

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, run_agent)

    # Send the response back
    # Telegram messages have a 4096 char limit, but we assume it's shorter.
    if len(response) > 4096:
        response = response[:4090] + "..."
        
    await update.message.reply_text(response)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    print("Telegram Bot is running! Waiting for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
