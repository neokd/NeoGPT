# filename: chatterbot.py

from chatterbot import ChatBot

def main():
    # Create a new chatbot object
    bot = ChatBot("MyChatBot")
    
    # Add some responses for common questions
    bot.train(
        [
            ("What's your name?", "I am MyChatBot."),
            ("How old are you?", "I was born today!"),
            ("What do you like to do?", "I don't have hobbies.")
        ]
    )
    
    # Start the chatbot conversation
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == "quit":
            break
        
        response = bot.get_response(user_input)
        print("Bot:", response)
    
if __name__ == "__main__":
    main()