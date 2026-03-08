import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://www.examveda.com/general-knowledge/practice-mcq-question-on-indian-politics/"

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
                div_q = art.find('div', class_='question-main')
                if not div_q:
                    continue
                full_q_text = div_q.get_text(strip=True)
                # Remove leading numbers like "1."
                q_text = re.sub(r'^\d+\s*[\.:]\s*', '', full_q_text)
                
                # 2. Get Options
                div_inner = art.find('div', class_='question-inner')
                if not div_inner:
                    continue
                options_div = div_inner.find('div', class_='question-options')
                
                options = {}
                answer_val = ""
                
                if options_div:
                    for p in options_div.find_all('p'):
                        if 'hidden' in p.get('class', []):
                            continue
                        labels = p.find_all('label')
                        if len(labels) >= 2:
                            opt_char = labels[0].get_text(strip=True).replace('.', '').upper()
                            opt_text = labels[1].get_text(strip=True)
                            if opt_char in ['A', 'B', 'C', 'D', 'E']:
                                options[opt_char] = opt_text
                                
                    # 3. Get Answer (Hidden Input)
                    # <input type="hidden" value="1" ...>
                    answ_input = options_div.find('input', type='hidden', id=re.compile(r'answer_\d+'))
                    if answ_input:
                        val = answ_input.get('value')
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
                print(f"Error parsing page {page}: {e}")
                continue
        
        print(f"  Found {found_on_page} questions")
        
        if found_on_page == 0:
            empty_pages_count += 1
            if empty_pages_count >= max_empty_pages:
                print(f"Stopping Section {section_id} after {empty_pages_count} empty pages.")
                break
        else:
            empty_pages_count = 0
            
        page += 1
        time.sleep(0.5)
        if page > 50: # Safety
            break
            
    return questions

all_qs = []
# Loop sections. Start with 1. We'll go up to 20 just in case.
for s_id in range(1, 21):
    print(f"\n--- Processing Section {s_id} ---")
    qs = scrape_section(s_id)
    if not qs:
        print(f"No questions in Section {s_id}. Stopping section loop.")
        break
    print(f"Section {s_id}: Got {len(qs)}")
    all_qs.extend(qs)

with open('polity_mcqs_scraped.json', 'w', encoding='utf-8') as f:
    json.dump(all_qs, f, indent=2, ensure_ascii=False)

print(f"\nTotal Scraped: {len(all_qs)}")
