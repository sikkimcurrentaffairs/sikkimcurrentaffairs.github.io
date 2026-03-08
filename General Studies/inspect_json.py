import json
from collections import Counter

data = json.load(open('biology_mcqs_scraped.json', encoding='utf-8'))
print(f"Total entries: {len(data)}")

texts = [d['text'] for d in data]
unique_texts = set(texts)
print(f"Unique texts: {len(unique_texts)}")

# Check for most common duplicates
counts = Counter(texts)
print("\nMost common duplicates:")
for text, count in counts.most_common(5):
    print(f"{count}x: {text[:50]}...")

# Check if sequences are repeating (e.g. page 1 content repeated)
print("\nFirst 3 questions:")
for i in range(3):
    print(f"{i}: {data[i]['text'][:100]}")

print("\nQuestion 10 (Page 2 start?):")
if len(data) > 10:
    print(f"10: {data[10]['text'][:100]}")

print("\nQuestion 100:")
if len(data) > 100:
    print(f"100: {data[100]['text'][:100]}")
