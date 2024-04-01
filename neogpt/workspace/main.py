# Import necessary libraries
import requests
from bs4 import BeautifulSoup

# Define the URL of the website we want to scrape
url = "https://www.google.com/search?q=go+love"

# Send a GET request to the website and retrieve its HTML content
response = requests.get(url)
html_content = response.text

# Parse the HTML content using Beautiful Soup
soup = BeautifulSoup(html_content, "html.parser")

# Find all the search result links and extract their URLs
search_links = soup.find_all("a", class_="yuRUbf")
urls = [link["href"] for link in search_links]

# Print out the URLs of the search results
print("Search Results URLs:")
for url in urls:
    print(url)