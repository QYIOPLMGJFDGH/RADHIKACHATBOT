from transformers import AutoModelForCausalLM, AutoTokenizer
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext, filters, Bot
import torch
import logging
import asyncio

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

# Function to handle incoming messages and generate response
async def handle_messages(client, update: Update):
    user_message = update.message.text  # Get the text from the user message
    chat_id = update.message.chat_id  # Get the chat ID

    # Log the user input for debugging
    logger.info(f"Received message from {chat_id}: {user_message}")

    try:
        # Generate the response from the Hugging Face model
        bot_response = generate_response(user_message)
        logger.info(f"Bot response: {bot_response}")

        # Send the bot's response back to the user
        await client.send_message(chat_id, bot_response)

    except Exception as e:
        # If there's an error, log it and send a generic response
        logger.error(f"Error occurred: {str(e)}")
        await client.send_message(chat_id, "Sorry, something went wrong. Please try again later.")

# Main function to run the bot
async def main():
    # Initialize the Telegram client
    client = Bot(token=TELEGRAM_BOT_TOKEN)

    # Register the message handler to reply to incoming messages
    client.add_handler(MessageHandler(filters.TEXT, handle_messages))

    # Start the bot
    await client.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
