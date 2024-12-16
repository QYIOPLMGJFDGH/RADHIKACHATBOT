from transformers import AutoModelForCausalLM, AutoTokenizer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters  # Corrected import statement
import torch
import logging

# Telegram Bot Token (BotFather se milta hai)
TELEGRAM_BOT_TOKEN = "7638229482:AAFBhF1jSnHqpTaQlpIx3YDfcksl_iqipFc"  # Yahan apna bot token daalein

# Load Hugging Face model
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Enable logging for better error tracking
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to generate response from the model
def generate_response(user_input: str):
    input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')

    # Generate a response
    with torch.no_grad():
        bot_output = model.generate(input_ids, max_length=150, pad_token_id=tokenizer.eos_token_id)

    # Decode the output and return the response
    bot_reply = tokenizer.decode(bot_output[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
    return bot_reply

# Function to handle messages from users
async def reply(update: Update, context: CallbackContext):
    user_message = update.message.text  # Get the text from the user message
    chat_id = update.message.chat_id  # Get the chat ID

    # Log the user input for debugging
    logger.info(f"Received message from {chat_id}: {user_message}")

    try:
        # Generate the response from the Hugging Face model
        bot_response = generate_response(user_message)
        logger.info(f"Bot response: {bot_response}")

        # Send the bot's response back to the user
        await update.message.reply_text(bot_response)

    except Exception as e:
        # If there's an error, log it and send a generic response
        logger.error(f"Error occurred: {str(e)}")
        await update.message.reply_text("Sorry, something went wrong. Please try again later.")

# Main function to run the bot
def main():
    # Create an Application object and provide the bot's token (using the new API)
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register a message handler for text messages (any text messages except commands)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # Start polling to get updates from Telegram
    application.run_polling()

if __name__ == "__main__":
    main()
