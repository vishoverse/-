from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import logging

# Setup logging to help debug issues
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Your OpenAI API key and Telegram Bot token
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace this with your OpenAI API key
BOT_TOKEN = '7929761558:AAFVWjNnIUP99XAVv0BNyNbvMnOSq8MoZEo'  # Your bot token

# Memory for conversation context (optional, simple memory for recent chat)
conversation_history = {}

# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I am विशाखा! How can I help you today?")

# Function to handle chat messages
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_msg = update.message.text

    # Add user message to memory
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_msg})

    # Generate response from OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history[user_id]
        )

        bot_reply = response['choices'][0]['message']['content']
        conversation_history[user_id].append({"role": "assistant", "content": bot_reply})

        # Send the bot's reply
        await update.message.reply_text(bot_reply)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        await update.message.reply_text("Oops! Something went wrong. Please try again later.")

# Command handler to reset the memory
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in conversation_history:
        del conversation_history[user_id]
    await update.message.reply_text("Memory reset successfully! Feel free to start over.")

# Inline button for additional options
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Reset Memory", callback_data='reset')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Need help? Here are some options:", reply_markup=reply_markup)

# Error handler to catch and log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# Main function to set up the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Add error handler
app.add_error_handler(error)

app.run_polling()
