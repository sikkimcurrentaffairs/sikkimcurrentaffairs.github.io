import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://www.examveda.com/general-knowledge/practice-mcq-question-on-biology/"

def get_soup(url):
    """Fetches URL and returns BeautifulSoup object."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            print(f"Failed to fetch {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def scrape_section(section_id):
    """Scrapes all pages for a specific section."""
    questions = []
    page = 1
    max_empty_pages = 2 
    empty_pages_count = 0
    
    while True:
        if section_id == 1:
            url = f"{BASE_URL}?page={page}"
        else:
            url = f"{BASE_URL}?section={section_id}&page={page}"
            
        print(f"Scraping Section {section_id} - Page {page}...")
        soup = get_soup(url)
        
        if not soup:
            break
            
        # Robust selection: Find all articles that are questions
        articles = soup.find_all('article', class_='question')
        
        found_on_page = 0
        
        for art in articles:
            try:
                # 1. Get Question Text
                # Text is consistently in div.question-main, regardless of h2 nesting
                q_main = art.find('div', class_='question-main')
                if not q_main:
                    continue
                
                full_q_text = q_main.get_text(strip=True)
                # Remove clean numbers: "1." "1 ." "123."
                # Also Remove "Question No : 1" if present (unlikely here but common in others)
                q_text = re.sub(r'^\d+\s*[\.:]\s*', '', full_q_text)
                
                # 2. Get Options
                # Consistently in div.question-inner -> div.question-options
                q_inner = art.find('div', class_='question-inner')
                if not q_inner:
                    continue
                
                options_div = q_inner.find('div', class_='question-options')
                options = {}
                answer_val = ""
                
                if options_div:
                    # Parse Options A, B, C, D
                    for p in options_div.find_all('p'):
                        if 'hidden' in p.get('class', []):
                            continue
                        
                        labels = p.find_all('label')
                        if len(labels) >= 2:
                            # First label is "A." usually
                            # Sometimes "A" without dot
                            opt_char = labels[0].get_text(strip=True).replace('.', '').upper().strip()
                            opt_text = labels[1].get_text(strip=True)
                            
                            if opt_char in ['A', 'B', 'C', 'D', 'E']:
                                options[opt_char] = opt_text
                                
                    # 3. Get Answer
                    # <input type="hidden" id="answer_5525" value="4" />
                    answ_input = options_div.find('input', type='hidden', id=re.compile(r'answer_\d+'))
                    if answ_input:
                        val = answ_input.get('value')
                        # Map 1->A, 2->B, 3->C, 4->D, 5->E
                        mapping = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E'}
                        answer_val = mapping.get(val, '')
                
                if q_text and options and answer_val:
                    questions.append({
                        'text': q_text,
                        'options': options,
                        'answer': answer_val,
                        'section': section_id,
                        'page': page
                    })
                    found_on_page += 1
                    
            except Exception as e:
                print(f"Error parsing question on page {page}: {e}")
                continue
        
        print(f"  Found {found_on_page} questions on page {page}")
        
        if found_on_page == 0:
            empty_pages_count += 1
            if empty_pages_count >= max_empty_pages:
                print(f"Stopping Section {section_id} after {empty_pages_count} empty pages.")
                break
        else:
            empty_pages_count = 0
            
        page += 1
        time.sleep(0.5)
        
        # Absolute safety limit
        if page > 60:
            break
            
    return questions

all_questions = []

# Scrape all 12 sections
for sec_id in range(1, 13):
    print(f"\n--- Processing Section {sec_id} ---")
    qs = scrape_section(sec_id)
    print(f"Section {sec_id}: Total {len(qs)} questions")
    all_questions.extend(qs)

# Save raw scraped data
with open('biology_mcqs_scraped.json', 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, indent=2, ensure_ascii=False)

print(f"\nTotal Scraped: {len(all_questions)}")
print("Saved to biology_mcqs_scraped.json")
