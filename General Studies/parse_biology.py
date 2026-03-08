"""
Biology MCQ Extractor & HTML Generator - Robust Version
Extracts MCQs from biology.pdf and generates HTML quiz files.
"""
import fitz
import re
import json
import os

# ============================================================
# STEP 1: Extract text and find answer blocks
# ============================================================
doc = fitz.open('biology.pdf')
full_text = ""
for page in doc:
    full_text += page.get_text() + "\n"
doc.close()

lines = full_text.split('\n')
print(f"Total lines: {len(lines)}")

answer_indices = []
for i, line in enumerate(lines):
    s = line.strip()
    if s.startswith('Answers') and len(s) < 20:
        answer_indices.append(i)

print(f"Answer blocks: {len(answer_indices)}")

# ============================================================
# STEP 2: Define sections manually with correct boundaries
# Each section is: title, question_start, question_end (= answer block line)
# The answer key follows immediately after question_end
# ============================================================

# Based on comprehensive manual analysis:
# The PDF has sections separated by "Answers" blocks.
# After the answer key, there may be a section title then new questions.

# Let me define sections based on what we know:
# Questions from line X to answer_indices[Y]
# Answer key from answer_indices[Y]+1 to next section start

section_defs = [
    {"title": "Botany and Branches", "q_start": 3, "ans_line": 234},
    {"title": "Classification of Plant Kingdom", "q_start": 281, "ans_line": 420},
    {"title": "Micro-organism (Virus, Bacteria, Fungi, Algae)", "q_start": 445, "ans_line": 4546},
    {"title": "Plant Physiology", "q_start": 4570, "ans_line": 4748},
    {"title": "Plant Disease and Agriculture", "q_start": 4790, "ans_line": 5124},
    {"title": "Classification of Animal Kingdom", "q_start": 5179, "ans_line": 7492},
    {"title": "Human Body Systems", "q_start": 7550, "ans_line": 9064},
    {"title": "Cell Biology (Cytology)", "q_start": 9120, "ans_line": 9689},
    {"title": "Animal Tissue", "q_start": 9750, "ans_line": 9957},
    {"title": "Health, Disease and Nutrition", "q_start": 9993, "ans_line": 12292},
    {"title": "Genetics and Evolution", "q_start": 12350, "ans_line": 12696},
    {"title": "Ecology", "q_start": 12747, "ans_line": 13223},
    {"title": "Environmental Pollution", "q_start": 13280, "ans_line": 13658},
    {"title": "Scientists, Discoveries and Biodiversity", "q_start": 13720, "ans_line": 14507},
    {"title": "Biotechnology", "q_start": 14548, "ans_line": 14850},
]

# ============================================================
# STEP 3: Parse answer keys
# ============================================================
def parse_answer_key(text_lines):
    """Parse answer key - join all lines and find N. (x) patterns."""
    text = ' '.join([l.strip() for l in text_lines])
    # Normalize brackets
    text = text.replace('{', '(').replace('}', ')').replace('[', '(').replace(']', ')')
    
    answers = {}
    # Try multiple patterns for OCR flexibility
    for m in re.finditer(r'(\d+)\s*[\.\,]\s*\(?([a-dA-D])\)?', text):
        q_num = int(m.group(1))
        ans = m.group(2).lower()
        if q_num not in answers and q_num < 300:
            answers[q_num] = ans
    
    return answers

# ============================================================
# STEP 4: Parse questions - very tolerant of OCR noise
# ============================================================
def parse_questions_robust(text_lines):
    """Parse questions and options with high OCR tolerance."""
    questions = []
    
    # Join all lines into one big text block, preserving line breaks
    # Then split on question number patterns
    
    # First pass: identify question start positions
    q_positions = []  # (line_index_in_text_lines, question_number, rest_of_line)
    
    for i, line in enumerate(text_lines):
        stripped = line.strip()
        if not stripped:
            continue
        
        # Remove leading OCR noise
        cleaned = re.sub(r'^[~\-:*.*<>=!@#$%^&\s]+', '', stripped)
        
        # Skip known non-question lines
        if cleaned in ['Biology', 'Objective General Knowledge', '---PAGE_BREAK---', '']:
            continue
        if re.match(r'^\d{3}$', cleaned):  # page numbers like 505, 506
            continue
        
        # Match question number at start of line: "N." or "N ."
        m = re.match(r'^(\d+)\s*\.\s*(.*)', cleaned)
        if m:
            q_num = int(m.group(1))
            rest = m.group(2).strip()
            
            # Filter: question numbers should be reasonable
            if q_num < 300:
                q_positions.append((i, q_num, rest))
    
    # Second pass: for each question, collect text until next question
    for pos_idx, (line_idx, q_num, first_line) in enumerate(q_positions):
        # Determine where this question's text ends
        if pos_idx + 1 < len(q_positions):
            next_line_idx = q_positions[pos_idx + 1][0]
        else:
            next_line_idx = len(text_lines)
        
        # Collect all lines for this question
        q_text_lines = []
        if first_line:
            q_text_lines.append(first_line)
        
        for j in range(line_idx + 1, next_line_idx):
            s = text_lines[j].strip()
            if s and s not in ['---PAGE_BREAK---', 'Biology', 'Objective General Knowledge']:
                if not re.match(r'^\d{3}$', s):
                    # Clean OCR noise
                    s = re.sub(r'^[~\-:*.*<>=!@#$%^&\s]+', '', s)
                    if s:
                        q_text_lines.append(s)
        
        # Now parse question text and options from q_text_lines
        full_text = ' '.join(q_text_lines)
        
        # Find options (a), (b), (c), (d) patterns
        # Options can appear as: (a) text  or  a) text  or  (a text
        option_pattern = r'[\(\{]?\s*([a-dA-D])\s*[\)\}]\s*'
        
        # Split by option markers
        parts = re.split(r'(?:[\(\{]\s*[a-dA-D]\s*[\)\}])', full_text)
        opt_letters = re.findall(r'[\(\{]\s*([a-dA-D])\s*[\)\}]', full_text)
        
        if len(parts) >= 2 and len(opt_letters) >= 2:
            question_text = parts[0].strip()
            options = {}
            
            for k, letter in enumerate(opt_letters):
                if k + 1 < len(parts):
                    opt_text = parts[k + 1].strip()
                    # Clean option text - remove exam references
                    opt_text = re.sub(r'\[.*?\]', '', opt_text)
                    opt_text = re.sub(r'\{.*?\}', '', opt_text)
                    opt_text = opt_text.strip()
                    if opt_text:
                        options[letter.lower()] = opt_text
            
            # Clean question text
            question_text = re.sub(r'\[.*?\]', '', question_text)
            question_text = re.sub(r'\{.*?\}', '', question_text)
            question_text = question_text.strip()
            # Remove trailing dashes and noise
            question_text = re.sub(r'[\-~:]+$', '', question_text).strip()
            
            if question_text and len(options) >= 2:
                questions.append({
                    'num': q_num,
                    'text': question_text,
                    'options': options
                })
    
    return questions

# ============================================================
# STEP 5: Process each section
# ============================================================
all_sections = []

for sec in section_defs:
    title = sec['title']
    q_start = sec['q_start']
    ans_line = sec['ans_line']
    
    # Get question lines
    q_lines = lines[q_start:ans_line]
    
    # Get answer key lines (from after "Answers" to either next section or +100 lines)
    a_end = min(ans_line + 100, len(lines))
    a_lines = lines[ans_line + 1:a_end]
    
    # Parse
    questions = parse_questions_robust(q_lines)
    answers = parse_answer_key(a_lines)
    
    # Match answers to questions
    valid = []
    for q in questions:
        if q['num'] in answers:
            q['answer'] = answers[q['num']]
            # Check we have the correct answer option
            if q['answer'] in q['options']:
                # Need at least 3 options for a decent MCQ
                if len(q['options']) >= 3:
                    valid.append(q)
    
    print(f"{title}: parsed={len(questions)}, answers_found={len(answers)}, valid={len(valid)}")
    
    if valid:
        # Show first question sample
        vq = valid[0]
        q_preview = vq['text'][:60]
        print(f"  Sample: Q{vq['num']}: {q_preview}...")
    
    all_sections.append({
        'title': title,
        'questions': valid,
        'slug': re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
    })

# ============================================================
# STEP 6: Summary
# ============================================================
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
total = 0
for sec in all_sections:
    n = len(sec['questions'])
    total += n
    print(f"  {sec['title']}: {n} MCQs")
print(f"\n  TOTAL: {total} valid MCQs")

# Save to JSON
with open('biology_mcqs.json', 'w', encoding='utf-8') as f:
    json.dump(all_sections, f, indent=2, ensure_ascii=False)
print("Saved to biology_mcqs.json")
