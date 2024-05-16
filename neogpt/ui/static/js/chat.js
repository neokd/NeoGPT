// Array to store chat message history
let chatMessageHistory = [];

// Function to display messages in the chat interface
function displayMessage(role, message) {
    const messagesList = document.getElementById('chat-messages');

    // Create a list item element
    const listItem = document.createElement('li');
    listItem.classList.add('message-item', role === 'user' ? 'user' : 'bot');
    listItem.textContent = message;

    // Append the message to the chat interface
    messagesList.appendChild(listItem);
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
                        console.log('Received message:', parsedMessage);
                        // Add the received message to chat history
                        chatMessageHistory.push({ role: 'bot', message: parsedMessage });
                        // Display the received message in the chat interface
                        displayMessage('bot', parsedMessage);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Event listener for chat form submission
const chatForm = document.getElementById('chat-form');
const userMessageInput = document.getElementById('user-input');
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
