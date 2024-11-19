// static/script.js

document.addEventListener("DOMContentLoaded", function() {
    const userInputField = document.getElementById("user-input");
    userInputField.focus();

    // Character Count Display
    const charCountDisplay = document.createElement("div");
    charCountDisplay.id = "char-count";
    charCountDisplay.innerText = "0 / 256";
    document.getElementById("input-area").appendChild(charCountDisplay);

    userInputField.addEventListener("input", () => {
        const maxLength = 256;
        const currentLength = userInputField.value.length;
        charCountDisplay.innerText = `${currentLength} / ${maxLength}`;
    });
});

function sendMessage() {
    const userInputField = document.getElementById("user-input");
    const userInput = userInputField.value.trim();
    if (userInput === "") return;

    // Display user message
    const chatLog = document.getElementById("chat-log");
    const userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.innerHTML = `<div class="text">${parseEmojis(userInput)}</div>`;
    chatLog.appendChild(userMessage);
    userInputField.value = "";
    scrollChatToBottom();

    // Show typing indicator
    showTypingIndicator();

    // Send message to server
    fetch("/get_response", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `user_input=${encodeURIComponent(userInput)}`
    })
    .then(response => response.json())
    .then(data => {
        // Hide typing indicator
        hideTypingIndicator();

        // Notify user if message was truncated
        if (data.truncated) {
            alert("Your message was too long and has been truncated.");
        }

        // Display bot response
        const botMessage = document.createElement("div");
        botMessage.className = "message bot";
        botMessage.innerHTML = `
            <div class="avatar">
                <img src="${avatarUrl}" alt="AIloha Avatar">
            </div>
            <div class="text">${parseEmojis(data.response)}</div>`;
        chatLog.appendChild(botMessage);
        scrollChatToBottom();
    })
    .catch(error => {
        console.error('Error:', error);
        hideTypingIndicator();
    });
}

function scrollChatToBottom() {
    const chatLog = document.getElementById("chat-log");
    chatLog.scrollTop = chatLog.scrollHeight;
}

function parseEmojis(text) {
    // Replace emoticons with emojis
    return text
        .replace(/:\)/g, '😊')
        .replace(/:\(/g, '☹️')
        .replace(/:D/g, '😃')
        .replace(/<3/g, '❤️')
        .replace(/;\)/g, '😉')
        .replace(/:P/g, '😜')
        .replace(/:\|/g, '😐');
}

// Typing Indicator Functions
function showTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    typingIndicator.style.display = 'block';
    scrollChatToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById("typing-indicator");
    typingIndicator.style.display = 'none';
}

// Get the avatar URL from the data attribute
const chatLog = document.getElementById("chat-log");
const avatarUrl = chatLog.getAttribute('data-avatar-url');

// Optional: Send a welcome message when the page loads
window.onload = function() {
    const chatLog = document.getElementById("chat-log");
    const botMessage = document.createElement("div");
    botMessage.className = "message bot";
    botMessage.innerHTML = `
        <div class="avatar">
            <img src="${avatarUrl}" alt="AIloha Avatar">
        </div>
        <div class="text">Hi there! I'm AIloha, your bubbly anime companion. 😊 How can I assist you today?</div>`;
    chatLog.appendChild(botMessage);
    scrollChatToBottom();
};
