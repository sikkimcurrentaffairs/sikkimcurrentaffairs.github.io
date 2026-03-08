import requests
import re

url = "https://www.examveda.com/general-knowledge/practice-mcq-question-on-biology/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        print(f"Content length: {len(content)}")
        print("First 500 chars:")
        print(content[:500])
        
        # Check for answer pattern
        if "Answer & Solution" in content:
            print("\nFound 'Answer & Solution' text.")
        
        # Look for hidden inputs or answer keys
        # Pattern: <div class="page-content">...
        # Let's search for the specific question "Ordinary table salt"
        if "Ordinary table salt" in content:
            print("\nFound question text.")
            
            # Extract the block around it
            start = content.find("Ordinary table salt")
            end = content.find("Save for Later", start)
            block = content[start:end+200]
            print("\nBlock around question:")
            print(block)
            
        else:
            print("\nQuestion text NOT found.")
            
    else:
        print("Failed to retrieve content.")

except Exception as e:
    print(f"Error: {e}")
