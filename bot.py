from transformers import AutoModelForCausalLM, AutoTokenizer
from pyrogram import Client, filters
import torch
import logging

# Telegram API credentials (replace with your own)
api_id = "16457832"  # Your API ID
api_hash = "3030874d0befdb5d05597deacc3e83ab"  # Your API Hash
bot_token = "7638229482:AAFBhF1jSnHqpTaQlpIx3YDfcksl_iqipFc"  # Your Bot Token from BotFather

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
async def handle_message(client, message):
    user_message = message.text  # Get the text from the user message
    chat_id = message.chat.id  # Get the chat ID

    # Log the user input for debugging
    logger.info(f"Received message from {chat_id}: {user_message}")

    try:
        # Generate the response from the Hugging Face model
        bot_response = generate_response(user_message)
        logger.info(f"Bot response: {bot_response}")

        # Send the bot's response back to the user
        await message.reply(bot_response)

    except Exception as e:
        # If there's an error, log it and send a generic response
        logger.error(f"Error occurred: {str(e)}")
        await message.reply("Sorry, something went wrong. Please try again later.")

# Create and run the client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Add message handler to respond to incoming messages
app.add_handler(filters.text, handle_message)

# Start the bot
if __name__ == "__main__":
    app.run()
