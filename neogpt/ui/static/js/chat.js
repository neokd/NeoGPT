// Array to store chat message history
let chatMessageHistory = [];

// Function to display messages in the chat interface
function displayMessage(role, message, isStreaming = false) {
    const messagesList = document.getElementById('chat-messages');

    // Create a list item element
    const listItem = document.createElement('li');
    listItem.classList.add('message-item');
    
    // Add additional classes based on the message role
    if (role === 'user') {
        listItem.classList.add('justify-end', 'text-right', 'flex', 'max-w-4xl', 'items-center','bg-gray-300', 'rounded-lg', 'dark:bg-neutral-700', 'p-4');
    } else {
        listItem.classList.add('justify-start', 'text-left', 'flex', 'max-w-4xl', 'items-center', 'mb-4', 'bg-white', 'shadow-lg', 'rounded-lg', 'dark:bg-neutral-900', 'p-4');
    }

    // Render the message using the marked library
    listItem.innerHTML = marked.parse(message);

    if (isStreaming) {
        listItem.setAttribute('id', 'streaming-message');
    }

    // Append the message to the chat interface
    messagesList.appendChild(listItem);
    messagesList.scrollTop = messagesList.scrollHeight; // Scroll to the bottom

    // Highlight code blocks using Prism
    Prism.highlightAllUnder(listItem);
}

// Function to update the last message in the chat interface
function updateLastMessage(message) {
    const streamingMessage = document.getElementById('streaming-message');

    if (streamingMessage) {
        streamingMessage.innerHTML = marked.parse(streamingMessage.textContent + message);

        // Highlight code blocks using Prism
        Prism.highlightAllUnder(streamingMessage);
    }
}

// Function to send user's message to the backend API
async function sendMessage(message) {
    // Add user's message to chat history
    chatMessageHistory.push({ role: 'user', message: message });

    // Display user's message in the chat interface
    displayMessage('user', message);

    try {
        const response = await fetch('/v1/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body.getReader();
        let partialMessage = '';

        // Display an empty bot message for streaming
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
                        // Add the received message to chat history
                        chatMessageHistory.push({ role: 'bot', message: parsedMessage.content });
                        // Update the last message in the chat interface
                        updateLastMessage(parsedMessage.content);
                    }
                }
            } else {
                updateLastMessage(partialMessage);
            }
        }

        // Remove the streaming-message ID after the response is complete
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
const regenerateButton = document.getElementById('regenerate-button');

chatForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const prompt = userMessageInput.value.trim();
    if (prompt !== '') {
        // Send the user's message
        sendMessage(prompt);
        // Clear the input field
        userMessageInput.value = '';
    }
});

// Event listener for regenerate button
// regenerateButton.addEventListener('click', (e) => {
//     // Get previous user input from chat history
//     const lastUserMessage = chatMessageHistory[chatMessageHistory.length - 1];
//     if (lastUserMessage) {
//         // Send the user's message
//         sendMessage(lastUserMessage.message);
//     }
// });
