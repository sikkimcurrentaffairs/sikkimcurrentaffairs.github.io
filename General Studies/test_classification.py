from process_biology_mcqs import classify_question
import json

with open('dummy_scraped.json', 'r') as f:
    questions = json.load(f)
    
print("Testing Classification Logic:\n")

for q in questions:
    cat = classify_question(q['text'])
    print(f"Q: {q['text'][:40]}... -> {cat}")
