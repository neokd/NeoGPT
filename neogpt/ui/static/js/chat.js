// Define chatMessageHistory at the top level
let chatMessageHistory = [];

// Function to save chat history to sessionStorage
function saveChatHistory() {
    sessionStorage.setItem('chatMessageHistory', JSON.stringify(chatMessageHistory));
}

// Function to load chat history from sessionStorage
function loadChatHistory() {
    const history = sessionStorage.getItem('chatMessageHistory');
    if (history) {
        chatMessageHistory = JSON.parse(history);
        chatMessageHistory.forEach(({ role, message }) => {
            displayMessage(role, message);
        });
    }
}

// Function to display messages in the chat interface
function displayMessage(role, message, isStreaming = false) {
    const messagesList = document.getElementById('chat-messages');
    let listItem;

    if (isStreaming) {
        listItem = document.getElementById('streaming-message');
        if (!listItem) {
            listItem = document.createElement('li');
            listItem.setAttribute('id', 'streaming-message');
            messagesList.appendChild(listItem);
        }
    } else {
        listItem = document.createElement('li');
    }

    listItem.classList.add('message-item');

    // Create a heading element for the role
    const heading = document.createElement('h4');
    heading.classList.add('text-md', 'font-semibold', 'text-gray-600', 'dark:text-neutral-300', 'mb-2');
    if (role === 'user') {
        heading.textContent = 'User:';
        listItem.classList.add('justify-start', 'text-left', 'flex', 'flex-col', 'max-w-4xl', 'items-start', 'mb-2', 'bg-white', 'shadow-lg', 'rounded-lg', 'dark:bg-neutral-700', 'p-4', 'bg-gray-300');
    } else {
        heading.textContent = 'NeoGPT:';
        listItem.classList.add('justify-start', 'text-left', 'flex', 'flex-col', 'max-w-4xl', 'items-start', 'mb-2', 'bg-white', 'shadow-lg', 'rounded-lg', 'dark:bg-neutral-900', 'p-4');
    }

    // Copy button with inline SVG
    const copyButton = document.createElement('button');
    copyButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
            <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
        </svg>
    `;
    copyButton.classList.add('copy-button', 'ml-auto', 'text-sm', 'text-gray-500', 'hover:text-red-500', 'dark:text-gray-600', 'dark:hover:text-red-500', 'duration-200', 'cursor-pointer');
    copyButton.addEventListener('click', () => {
        navigator.clipboard.writeText(message).then(() => {
            copyButton.innerHTML = 'Copied!';
            setTimeout(() => {
                copyButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy">
                        <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                        <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
                    </svg>
                `;
            }, 1000);
        });
    });

    // Create a timestamp element
    const now = new Date();
    const formattedTime = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    heading.textContent += ` ${formattedTime}`;

    // Render the message using the marked library
    const messageContent = document.createElement('div');
    messageContent.innerHTML = marked.parse(message.replace(/\n\n/g, '<br><br>'));

    listItem.innerHTML = '';
    listItem.appendChild(heading);
    listItem.appendChild(messageContent);
    listItem.appendChild(copyButton);

    if (!isStreaming) {
        messagesList.appendChild(listItem);
    }

    Prism.highlightAllUnder(listItem);
    messageContent.scrollIntoView({ behavior: 'smooth' });
}

// Function to update the last message in the chat interface
function updateLastMessage(message) {
    const streamingMessage = document.getElementById('streaming-message');

    if (streamingMessage) {
        const messageContent = streamingMessage.querySelector('div');
        messageContent.innerHTML = marked.parse(messageContent.textContent.replace(/\n\n/g, '<br><br>') + message.replace(/\n\n/g, '<br><br>'));
        Prism.highlightAllUnder(streamingMessage);
    }
}

// Function to send user's message to the backend API
async function sendMessage(message) {
    chatMessageHistory.push({ role: 'user', message: message });
    saveChatHistory();

    displayMessage('user', message);

    try {
        const response = await fetch('/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body.getReader();
        let partialMessage = '';
        let botMessage = '';

        displayMessage('bot', '', true);

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                break;
            }
            const chunk = new TextDecoder().decode(value);
            partialMessage += chunk;

            if (partialMessage.includes('\n')) {
                const messages = partialMessage.split('\n');
                partialMessage = messages.pop();
                for (const message of messages) {
                    if (message) {
                        const parsedMessage = JSON.parse(message);
                        botMessage += parsedMessage.content;
                        updateLastMessage(parsedMessage.content);
                    }
                }
            } else {
                updateLastMessage(partialMessage);
            }
        }

        // Finalize the bot message and store it
        if (partialMessage) {
            const parsedMessage = JSON.parse(partialMessage);
            botMessage += parsedMessage.content;
        }

        chatMessageHistory.push({ role: 'bot', message: botMessage });
        saveChatHistory();

        const streamingMessage = document.getElementById('streaming-message');
        if (streamingMessage) {
            streamingMessage.removeAttribute('id');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Event listener for chat form submission
const chatForm = document.getElementById('chat-form');
const userMessageInput = document.getElementById('chat-input');
// Event listener for regenerate button
const regenerateButton = document.getElementById('regenerate-response');

chatForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const prompt = userMessageInput.value;
    if (prompt !== '') {
        sendMessage(prompt);
        userMessageInput.value = '';
    }
});

// Event listener for regenerate button
regenerateButton.addEventListener('click', () => {
    const lastUserMessage = chatMessageHistory.slice().reverse().find(message => message.role === 'user');
    if (lastUserMessage) {
        sendMessage(lastUserMessage.message);
    }
});

// Load chat history from sessionStorage when the page loads
window.addEventListener('load', loadChatHistory);

// Monitor chat messages and display logo placeholder when empty
document.addEventListener("DOMContentLoaded", function() {
    const chatMessages = document.getElementById("chat-messages");
    const logoPlaceholder = document.getElementById("logo-placeholder");

    function checkChatMessages() {
        if (chatMessages.children.length === 0) {
            logoPlaceholder.style.display = "flex";
        } else {
            logoPlaceholder.style.display = "none";
        }
    }

    // Initially check the chat messages
    checkChatMessages();

    // Check chat messages on any change
    const observer = new MutationObserver(checkChatMessages);
    observer.observe(chatMessages, { childList: true });

    // Handle form submission
    const chatForm = document.getElementById("chat-form");
    chatForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const chatInput = document.getElementById("chat-input");
        const newMessage = document.createElement("li");
        newMessage.textContent = chatInput.value;
        chatMessages.appendChild(newMessage);
        chatInput.value = "";
    });
});
