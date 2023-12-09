import secrets

import streamlit as st


def generate_password(length):
    password = (
        (
            secrets.token_hex(length)
            + secrets.token_hex(length)
            + secrets.token_hex(length)
        )
        .replace("\n", "")
        .strip()
    )
    return password


if __name__ == "__main__":
    st.title("Strong Password Generator")
    st.write("Enter the desired password length:")

    # Get the user input for password length
    length_input = st.text_input(label="Enter length")

    if length_input:
        # Check if the input is not empty
        length = int(length_input)

        if length < 8:
            st.write("Password length should be at least 8 characters.")
        else:
            password = generate_password(length)
            st.write(f"Generated Password: {password}")
    else:
        st.write("Please enter a valid password length.")
