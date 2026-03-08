import requests
from bs4 import BeautifulSoup
import re

url = "https://www.examveda.com/general-knowledge/practice-mcq-question-on-biology/?section=4"
headers = {
    "User-Agent": "Mozilla/5.0"
}

print(f"Checking {url}...")
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

articles = soup.find_all('article')
print(f"Found {len(articles)} articles.")

for i, art in enumerate(articles):
    classes = art.get('class', [])
    print(f"\nArticle {i} classes: {classes}")
    # Print a snippet of content
    print(art.prettify()[:200])
