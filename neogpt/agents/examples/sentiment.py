# Import required libraries
import streamlit as st
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Define the app layout with input boxes and dropdowns for model selection
st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("Sentiment Analysis")
st.subheader("Enter text to analyze sentiment")

text_input = st.text_area("Text Input", value="", max_chars=200)
model_select = st.selectbox("Select a model:", ["TextBlob", "VADER"], index=0)
submit_button = st.button("Submit")


# Define the function to implement the sentiment analysis task using the selected model
def analyze_sentiment(text, model):
    if model == "TextBlob":
        blob = TextBlob(text)
        return blob.sentiment.polarity
    elif model == "VADER":
        analyzer = SentimentIntensityAnalyzer()
        return analyzer.polarity_scores(text)["compound"]


# Implement the sentiment analysis task using the selected model when the submit button is clicked
if submit_button:
    if text_input:
        sentiment = analyze_sentiment(text_input, model_select)
        st.subheader("Sentiment Analysis Result")
        if sentiment >= 0.5:
            result = "Positive"
        elif sentiment <= -0.5:
            result = "Negative"
        else:
            result = "Neutral"
        st.write(result)
    else:
        st.write("Please enter text to analyze sentiment")
