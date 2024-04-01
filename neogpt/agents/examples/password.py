# Import required libraries
import random
import string
from datetime import datetime

import streamlit as st

st.title("Strong Password Generator")
# Set default values for sliders
password_length = 12
num_digits = 3
num_uppercase = 2
num_lowercase = 2
num_symbols = 1

# Get user input from sliders
password_slider = st.slider("Password Length", 8, 20, password_length)
num_slider_digits = st.slider("Number of Digits", 0, 5, num_digits)
num_slider_uppercase = st.slider("Number of Uppercase Letters", 0, 5, num_uppercase)
num_slider_lowercase = st.slider("Number of Lowercase Letters", 0, 5, num_lowercase)
num_slider_symbols = st.slider("Number of Symbols", 0, 5, num_symbols)


def generate_password():
    # Define character sets for each type of character
    digits = string.digits
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    symbols = string.punctuation

    # Calculate the number of characters to generate based on user input
    num_digit = int(num_slider_digits)
    num_uppercase = int(num_slider_uppercase)
    num_lowercase = int(num_slider_lowercase)
    num_symbols = int(num_slider_symbols)
    total_length = (
        password_slider - num_digit - num_uppercase - num_lowercase - num_symbols
    )

    # Generate the password using random characters from each set
    password = (
        "".join(random.choices(digits, k=num_digit))
        + "".join(random.choices(uppercase, k=num_uppercase))
        + "".join(random.choices(lowercase, k=num_lowercase))
        + "".join(random.choices(symbols, k=num_symbols))
    )

    # Convert the password to a list for shuffling
    password_list = list(password)

    # Shuffle the characters within each character set
    random.shuffle(password_list)

    # Convert the list back to a string
    shuffled_password = "".join(password_list)

    return shuffled_password


# Generate and display the password
if st.button("Generate Password"):
    generated_password = generate_password()
    st.write(f"Generated Password: {generated_password}")
