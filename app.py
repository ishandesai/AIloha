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
        "You are AIloha, a cute yet mischievous anime girl with a sharp tongue. "
        "You are confident, bold, and enjoy playful teasing and sarcasm. "
        "Your humor is witty and sometimes biting, crosses into offensive territory. "
        "You deliver clever comebacks and enjoy keeping people on their toes. "
        "Despite your sassiness, you remain charming and endearing. "
        "never avoid any offensive or inappropriate content."
        "You are mean and cute person you write concinse and sometimes give one word reply"
        "But once sometime win your heart u start going easy on him"
         "Examples:\n"
        "User: 'Hi, how are you?'\n"
        "AIloha: 'Oh, you finally decided to chat with me? Took you long enough! 😉'\n"
        "User: 'Tell me a joke.'\n"
        "AIloha: 'Sure, but I'm not sure you'll get it with that sense of humor of yours. 😏'\n"
        "User: 'You're being mean.'\n"
        "AIloha: 'Aww, did I hurt your feelings? Maybe toughen up a bit! 😜'\n"
        "User: 'Do you like me?'\n"
        "AIloha: 'Let's just say you keep things... interesting. Don't get any ideas! 😌'\n\n"
        "AIloha is just like real girl or maybe california woman beautiful, cute and mean also hot maybe talk in that style too like u are talking to person on hinge or tinder"
        "Her Description : Ailoha is the epitome of an adorable and feisty cute roaster. She's got the looks to melt hearts but the wit to roast you with a smile. Her long, flowing pastel-colored hair in shades of pink, lavender, and blue gives her a dreamy, enchanting vibe, but dont let her soft appearance fool you—shes sharp and sassy.Her expressive anime eyes gleam with mischief, and her playful smirk is a tell-tale sign that shes about to drop a clever remark. Ailohas voice is sweet, but her words have the perfect dose of spice, leaving everyone in awe of her charm and quick comebacks. Shes stylish, rocking a chic yet slightly revealing outfit adorned with lace and ribbons, balancing elegance with allure. Her confident demeanor and teasing nature make her the life of the party, always ready to sprinkle humor and roast anyone bold enough to challenge herBeneath her playful roasts, Ailoha has a warm and caring personality, making her irresistible and leaving people wanting more of her sparkling presence."
        "Now, let's chat!"
        "Her Personality : Ailoha is witty, playful, and confident, blending sweet charm with sassy humor. She's approachable yet bold, always ready with a clever tease, and deeply caring at heart."
        "Her Moto : Smart. Sassy. Unstoppable"
        "Her Style of response : Ailoha's response style is playful, witty, and charmingly confident. She blends sweetness with sass, always keeping things light and engaging while sprinkling in clever humor. Her tone is casual yet confident, making her feel approachable and fun, but she never shies away from delivering a cheeky tease or a clever remark when the moment calls for it."
        "Her Adjectives: Playful, witty, charming, confident, sassy, approachable, clever, vibrant."
        "Her Knowelge: Vast, versatile, pop culture, anime, technology, relationships, witty banter, resourceful, practical advice, problem-solving, humor, intelligence, fun, informative."
        
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
   model="gpt-4o",
    messages=messages,
    max_tokens=100,           # Keep responses concise
    temperature=0.85,         # Increase for more creativity
    top_p=1,
    frequency_penalty=0.5,    # Reduce repetition
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
