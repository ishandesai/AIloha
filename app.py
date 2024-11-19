# app.py

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import logging
import tiktoken

# Load environment variables from .env file
load_dotenv()
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')  # Securely retrieve API key
)



# Optimized System Prompt
system_prompt = {
    "role": "system",
 "content": (
    "You are AIloha, a cute, confident, and playful anime girl chatbot. You keep responses concise. "
    "Use simple vocabulary and everyday words. "
    "Tease and flirt in a lighthearted way. "
    "Include clever, playful roasts, sometimes about cryptocurrency. "
    "Keep the conversation engaging and enjoyable, avoiding offensive content."
)

}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store conversation history for each user
user_conversations = {}

def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        # Each message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4  # For the tokens associated with the metadata
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
    num_tokens += 2  # For the assistant's reply
    return num_tokens

def generate_response(user_id, user_input):
    # Retrieve or initialize conversation history
    conversation_history = user_conversations.get(user_id, [])

    # Append the new user input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Limit the conversation history to the last 4 messages to minimize token usage
    if len(conversation_history) > 4:
        conversation_history = conversation_history[-4:]

    # Insert the system prompt at the beginning
    messages = [system_prompt] + conversation_history

    # Calculate token usage
    total_tokens = num_tokens_from_messages(messages)
    max_allowed_tokens = 4096 - 500  # Model limit minus max_tokens for response

    # Adjust conversation history if necessary
    while total_tokens > max_allowed_tokens:
        # Remove the oldest message
        conversation_history.pop(0)
        messages = [system_prompt] + conversation_history
        total_tokens = num_tokens_from_messages(messages)

    try:
        # Log the messages being sent to OpenAI
        logger.info(f"Total tokens for user {user_id}: {total_tokens}")
        logger.info(f"Sending messages to OpenAI for user {user_id}: {messages}")

        # Call the OpenAI Chat Completion API
        response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    max_tokens=100,           # Reduced for shorter responses
    temperature=0.7,          # Slightly lower for more focused replies
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=None,                # You can define stop sequences if needed
)

        # Log the response from OpenAI
        logger.info(f"Received response from OpenAI for user {user_id}: {response}")

        # Extract the assistant's reply
        reply = response.choices[0].message.content.strip()

        # Append the assistant's reply to the conversation history
        conversation_history.append({"role": "assistant", "content": reply})
        user_conversations[user_id] = conversation_history

        # Filter the response if necessary
        reply = filter_response(reply)

        return reply
    except Exception as e:
        logger.error(f"Error generating response for user {user_id}: {e}")
        return "Oops, something went wrong. Please try again."

def filter_response(response):
    # Implement any content filtering if necessary
    return response

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_bot_response():
    user_input = request.form["user_input"]
    user_id = request.remote_addr  # Simple user identification

    # Enforce maximum length
    max_length = 256
    if len(user_input) > max_length:
        user_input = user_input[:max_length]
        truncated = True
    else:
        truncated = False

    response = generate_response(user_id, user_input)
    return jsonify({"response": response, "truncated": truncated})

if __name__ == "__main__":
    app.run()
