from flask import Flask, request, jsonify, render_template_string
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/chat/completions"

app = Flask(__name__)

# Initialize chat history (system role)
messages = [{"role": "system", "content": "You are a helpful assistant"}]

# AI chatbot logic using Groq API
def ai_chatbot_reply(user_message):
    global messages
    # Append user message
    messages.append({"role": "user", "content": user_message})

    # Prepare request
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 150
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Call Groq API
    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()

    if "choices" in resp_json:
        reply = resp_json["choices"][0]["message"]["content"]
        # Append AI response to history
        messages.append({"role": "assistant", "content": reply})
        return reply
    else:
        return f"API Error: {resp_json}"

# API Route
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data['message']
    bot_response = ai_chatbot_reply(user_message)
    return jsonify({"reply": bot_response})

# HTML form with high-level colorized UI
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chatbot</title>
    <style>
      body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #1f1c2c, #928dab);
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
        color: #fff;
      }

      .chat-container {
        background-color: rgba(0,0,0,0.7);
        border-radius: 15px;
        width: 400px;
        max-width: 90%;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        display: flex;
        flex-direction: column;
      }

      .messages {
        flex: 1;
        overflow-y: auto;
        margin-bottom: 15px;
      }

      .message {
        padding: 8px 12px;
        border-radius: 12px;
        margin-bottom: 10px;
        max-width: 80%;
        word-wrap: break-word;
      }

      .user {
        background: #4e9af1;
        align-self: flex-end;
      }

      .bot {
        background: #6c757d;
        align-self: flex-start;
      }

      input[type="text"] {
        padding: 10px 15px;
        border-radius: 20px;
        border: none;
        width: calc(100% - 50px);
        margin-right: 10px;
        outline: none;
      }

      button {
        padding: 10px 15px;
        border-radius: 50%;
        border: none;
        background-color: #ff6b6b;
        color: white;
        cursor: pointer;
        transition: 0.3s;
      }

      button:hover {
        background-color: #ff4757;
      }

      .input-container {
        display: flex;
        align-items: center;
      }

    </style>
    </head>
    <body>

    <div class="chat-container">
      <div class="messages" id="messages"></div>
      <div class="input-container">
        <input type="text" id="messageInput" placeholder="Type your message...">
        <button id="sendBtn">➤</button>
      </div>
    </div>

    <script>
      const messagesDiv = document.getElementById('messages');
      const input = document.getElementById('messageInput');
      const button = document.getElementById('sendBtn');

      function addMessage(text, className) {
        const msgDiv = document.createElement('div');
        msgDiv.textContent = text;
        msgDiv.className = 'message ' + className;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      }

      async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;
        addMessage(message, 'user');
        input.value = '';

        const res = await fetch('/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({message})
        });

        const data = await res.json();
        addMessage(data.reply, 'bot');
      }

      button.addEventListener('click', sendMessage);
      input.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
      });
    </script>

    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
