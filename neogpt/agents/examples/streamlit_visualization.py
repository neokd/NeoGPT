# filename: streamlit_visualization.py

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Load the iris dataset
iris = load_iris()
X = iris["data"]
y = iris["target"]

# Create a logistic regression model and fit it to the data
model = LogisticRegression(max_iter=1000)
model.fit(X, y)
st.set_option("deprecation.showPyplotGlobalUse", False)
st.title("Iris Dataset Visualization")
# Make predictions on the test set
y_pred = model.predict(X)


# Calculate the accuracy of the model
accuracy = accuracy_score(y, y_pred)
print("Accuracy:", accuracy)

# Get the classification report
classification_report_text = classification_report(y, y_pred)
print("\nClassification Report:\n", classification_report_text)

st.write("Classification Report:\n", classification_report_text)

# Create a scatter plot of the features and target variable
plt.scatter(X[:, 0], X[:, 1], c=y)
plt.xlabel("Sepal Length (cm)")
plt.ylabel("Sepal Width (cm)")
plt.title("Iris Dataset Visualization")
# plt.show()
st.subheader("Scatter Plot")
st.pyplot()

# Create a histogram of the target variable
plt.hist(y, bins=[0, 1, 2], align="left", rwidth=0.8)
plt.xlabel("Target Variable")
plt.title("Iris Dataset Visualization")
plt.show()
st.subheader("Histogram")
st.pyplot()
