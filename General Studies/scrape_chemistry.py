import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://www.examveda.com/general-knowledge/practice-mcq-question-on-chemistry/"

def scrape_page(section_id, page_id):
    url = f"{BASE_URL}?section={section_id}&page={page_id}"
    print(f"Scraping Section {section_id}, Page {page_id}: {url}", flush=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    questions = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch: Status {response.status_code}", flush=True)
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='question')
        
        if not articles:
            return []

        for art in articles:
            # Question Text
            q_main = art.find('div', class_='question-main')
            if not q_main: continue
            
            q_text = q_main.get_text(strip=True)
            
            # Options
            options = {}
            p_tags = art.find_all('p')
            for p in p_tags:
                label_tag = p.find('label')
                if label_tag:
                    text = p.get_text(strip=True)
                    if text.startswith('A.') or text.startswith('B.') or text.startswith('C.') or text.startswith('D.'):
                        key = text[0]
                        val = text[2:].strip()
                        options[key] = val
            
            # Answer
            answer_val = ""
            ans_input = art.find('input', id=lambda x: x and x.startswith('answer_'))
            if ans_input:
                answer_val = ans_input.get('value', '').upper()
            
            if q_text and options and answer_val:
                questions.append({
                    "text": q_text,
                    "options": options,
                    "answer": answer_val,
                    "section": section_id
                })
        
        return questions

    except Exception as e:
        print(f"Error: {e}", flush=True)
        return []

def main():
    all_qs = []
    # Scrape all 12 sections
    for s_id in range(1, 13):
        print(f"Starting Section {s_id}...", flush=True)
        for p_id in range(1, 15): # Max 140 questions per section
            qs = scrape_page(s_id, p_id)
            if not qs:
                break
            all_qs.extend(qs)
            print(f"  Page {p_id}: Added {len(qs)} questions. Total so far: {len(all_qs)}", flush=True)
            time.sleep(0.5) # Be nice
    
    print(f"\nTotal questions scraped: {len(all_qs)}", flush=True)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chemistry_mcqs_scraped.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_qs, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output_path}", flush=True)

if __name__ == "__main__":
    main()
