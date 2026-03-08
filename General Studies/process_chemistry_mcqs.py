import json
import os
import re

# Define Chemistry Categories and Keywords
CATEGORIES = {
    "Atomic Structure & Nuclear Chemistry": [
        "atom", "nucleus", "electron", "proton", "neutron", "isotope", "radioactivity", 
        "orbit", "valency", "quantum", "spectra", "radiation", "decay"
    ],
    "Chemical Bonding & Molecular Structure": [
        "bond", "molecule", "electronegativity", "ionic", "covalent", "metallic", 
        "valence", "hybridization", "polarity", "dipole"
    ],
    "Physical Chemistry": [
        "molality", "molarity", "thermodynamics", "kinetics", "rate", "pressure", 
        "gas", "liquid", "solution", "equilibrium", "enthalpy", "entropy"
    ],
    "Inorganic Chemistry & Metallurgy": [
        "metal", "non-metal", "metallurgy", "smelting", "roasting", "ore", "mineral", 
        "periodic table", "catalyst", "alkali", "halogen", "transition"
    ],
    "Organic Chemistry": [
        "organic", "carbon", "hydrocarbon", "polymer", "isomer", "alcohol", 
        "alkane", "alkene", "alkyne", "ester", "ether", "phenol"
    ],
    "Environmental Chemistry": [
        "global warming", "greenhouse", "ozone", "pollution", "waste", "atmosphere",
        "acid rain", "effluent", "smog"
    ],
    "Chemistry in Everyday Life": [
        "drug", "medicine", "detergent", "soap", "glass", "cement", "polymer", 
        "plastic", "fertilizer", "dye", "explosive"
    ]
}

def classify_question(text):
    text = text.lower()
    scores = {cat: 0 for cat in CATEGORIES}
    
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                scores[cat] += 1
                
    # Extra weight for specific terms
    if "atom" in text or "nuclear" in text: scores["Atomic Structure & Nuclear Chemistry"] += 0.5
    if "environmental" in text or "warming" in text: scores["Environmental Chemistry"] += 0.5
    
    best_cat = "General Chemistry"
    max_score = 0.5 # Minimum threshold
    
    for cat, score in scores.items():
        if score > max_score:
            max_score = score
            best_cat = cat
            
    return best_cat

def generate_quiz_html(title, questions, slug):
    """Generate a quiz HTML page."""
    
    quiz_data_items = []
    for q in questions:
        q_text_json = json.dumps(q['text'])
        
        opts_json = []
        for letter in ['A', 'B', 'C', 'D']:
            opt_val = q['options'].get(letter, '')
            opts_json.append(json.dumps(opt_val))
            
        ans_raw = str(q['answer']).strip().upper()
        if ans_raw.isdigit():
            answer_idx = int(ans_raw) - 1
        elif len(ans_raw) == 1 and 'A' <= ans_raw <= 'D':
            answer_idx = ord(ans_raw) - ord('A')
        else:
            answer_idx = 0 # Fallback
            
        if answer_idx < 0 or answer_idx > 3: answer_idx = 0 # Safety
        
        quiz_data_items.append(f'''            {{
                question: {q_text_json},
                options: [{', '.join(opts_json)}],
                answer: {answer_idx}
            }}''')
            
    quiz_data_js = ',\n'.join(quiz_data_items)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Sikkim PSC Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                    }},
                }}
            }}
        }}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }}
        .quiz-container {{
            max-width: 800px;
            margin: 20px auto;
            background: #fff;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        }}
        html.dark .quiz-container {{
            background: #24272c;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #0284c7;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        .question-block {{
            margin-bottom: 35px;
            padding-bottom: 20px;
            border-bottom: 1px solid #f1f5f9;
        }}
        html.dark .question-block {{
            border-bottom: 1px solid #334155;
        }}
        .question-text {{
            font-size: 1.15em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #1e293b;
        }}
        html.dark .question-text {{
            color: #f1f5f9;
        }}
        .options-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .option {{
            background-color: #f8fafc;
            border: 2px solid #e2e8f0;
            padding: 16px 20px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-weight: 500;
            color: #475569;
        }}
        html.dark .option {{
            background-color: #1e293b;
            border: 2px solid #334155;
            color: #cbd5e1;
        }}
        .option:hover {{
            background-color: #f1f5f9;
            border-color: #cbd5e1;
            transform: translateX(4px);
        }}
        html.dark .option:hover {{
            background-color: #334155;
            border-color: #475569;
        }}
        .option.correct {{
            background-color: #dcfce7 !important;
            border-color: #4ade80 !important;
            color: #166534 !important;
        }}
        html.dark .option.correct {{
            background-color: #064e3b !important;
            border-color: #10b981 !important;
            color: #ecfdf5 !important;
        }}
        .option.incorrect {{
            background-color: #fee2e2 !important;
            border-color: #f87171 !important;
            color: #991b1b !important;
        }}
        html.dark .option.incorrect {{
            background-color: #7f1d1d !important;
            border-color: #ef4444 !important;
            color: #fef2f2 !important;
        }}
        .options-list.answered .option {{
            cursor: default;
            pointer-events: none;
        }}
        .quiz-stats-badge {{
            background: #f1f5f9;
            color: #64748b;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 20px;
        }}
        html.dark .quiz-stats-badge {{
            background: #334155;
            color: #94a3b8;
        }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-slate-900 min-h-screen p-4 sm:p-8">

    <div class="quiz-container">
        <a href="chemistry.html" class="back-link">&larr; Back to Chemistry Topics</a>
        <h1 class="text-3xl font-bold text-sky-800 dark:text-sky-400 mb-2">{title}</h1>
        <div class="quiz-stats-badge">{len(questions)} MCQ Questions</div>
        
        <div id="questions-wrapper"></div>
    </div>

    <script>
        const quizData = [
{quiz_data_js}
        ];

        const wrapper = document.getElementById('questions-wrapper');

        quizData.forEach((item, index) => {{
            const questionBlock = document.createElement('div');
            questionBlock.className = 'question-block';

            const questionText = document.createElement('p');
            questionText.className = 'question-text';
            questionText.innerHTML = `<span class="text-sky-600 dark:text-sky-500 mr-2">Q${{index + 1}}.</span> ${{item.question}}`;
            questionBlock.appendChild(questionText);

            const optionsList = document.createElement('ul');
            optionsList.className = 'options-list';

            item.options.forEach((option, optionIndex) => {{
                if (!option || option.trim() === '') return;
                
                const optionItem = document.createElement('li');
                optionItem.className = 'option';
                optionItem.textContent = option;
                optionItem.dataset.index = optionIndex;

                optionItem.addEventListener('click', () => {{
                    if (optionsList.classList.contains('answered')) return;
                    optionsList.classList.add('answered');

                    const selectedAnswer = parseInt(optionItem.dataset.index);
                    const correctAnswer = item.answer;

                    if (selectedAnswer === correctAnswer) {{
                        optionItem.classList.add('correct');
                    }} else {{
                        optionItem.classList.add('incorrect');
                        optionsList.children[correctAnswer].classList.add('correct');
                    }}
                }});

                optionsList.appendChild(optionItem);
            }});

            questionBlock.appendChild(optionsList);
            wrapper.appendChild(questionBlock);
        }});

        // Theme sync
        if (localStorage.getItem('theme') === 'dark' || 
            (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.documentElement.classList.add('dark');
        }}
    </script>
</body>
</html>'''
    return html

def generate_landing_page(sections):
    """Generate landing page cards."""
    cards_html = ""
    colors = [
        ("rose", "600"), ("pink", "600"), ("fuchsia", "600"), ("purple", "600"),
        ("violet", "600"), ("indigo", "600"), ("blue", "600"), ("sky", "600"),
        ("cyan", "600"), ("teal", "600"), ("emerald", "600"), ("green", "600"),
    ]
    
    for i, sec in enumerate(sections):
        color = colors[i % len(colors)][0]
        title = sec['title']
        count = sec['count']
        filename = sec['filename']
        
        cards_html += f'''
                    <!-- {title} -->
                    <a href="{filename}"
                        class="quiz-card group block p-6 sm:p-8 fade-in-up focus:outline-none focus:ring-4 focus:ring-{color}-500/50">
                        <div class="flex flex-col items-center">
                            <div class="icon-bg mb-4 p-3 rounded-full group-hover:scale-110 transition-transform duration-300 bg-{color}-100 dark:bg-{color}-900/30">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="1.5" stroke="currentColor"
                                    class="w-8 h-8 text-{color}-600">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M9.75 3.104v1.607a2.1 2.1 0 01-.21.917l-4.227 8.455a2.1 2.1 0 00-.21.917v4.032a2.1 2.1 0 002.1 2.1h9.354a2.1 2.1 0 002.1-2.1v-4.032c0-.324-.074-.643-.21-.917l-4.227-8.455a2.1 2.1 0 01-.21-.917V3.104M9 3h6m-5 9h4m-5 3h4m-5 3h4" />
                                </svg>
                            </div>
                            <h2 class="text-xl sm:text-2xl font-semibold text-center mb-2 group-hover:text-{color}-600 dark:group-hover:text-{color}-400 transition-colors duration-300">
                                {title}</h2>
                            <p class="text-sm text-center mb-4 text-gray-500">{count} Questions</p>
                            <span class="inline-flex items-center justify-center px-5 py-2.5 text-sm font-medium text-white bg-{color}-600 rounded-lg group-hover:bg-{color}-700 transition-all duration-300 transform group-hover:scale-105 shadow-md">
                                Start Practice
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="2" stroke="currentColor" class="w-4 h-4 ml-2">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                                </svg>
                            </span>
                        </div>
                    </a>
'''
    html = f'''<!DOCTYPE html>
<html lang="en" class="">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chemistry MCQs | Sikkim PSC Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                    }},
                }}
            }}
        }}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }}
        .quiz-card {{
            background: #eef1f5;
            border-radius: 24px;
            box-shadow: 10px 10px 20px #d1d9e6, -10px -10px 20px #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }}
        .quiz-card:hover {{
            box-shadow: 14px 14px 28px #d1d9e6, -14px -14px 28px #ffffff;
            transform: translateY(-4px);
        }}
        html.dark .quiz-card {{
            background: #24272c;
            box-shadow: 10px 10px 20px #16181b, -10px -10px 20px #32363d;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        html.dark .quiz-card:hover {{
            box-shadow: 14px 14px 28px #16181b, -14px -14px 28px #32363d;
        }}
        .fade-in-up {{
            animation: fadeInUp 0.6s ease-out forwards;
            opacity: 0;
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .icon-bg {{
            background: rgba(255,255,255,0.5);
        }}
        html.dark .icon-bg {{
            background: rgba(255,255,255,0.1);
        }}
    </style>
</head>
<body class="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <div class="max-w-6xl mx-auto px-4 py-8 sm:py-12">
        <div class="mb-8">
            <a href="../index.html" class="text-sky-600 dark:text-sky-400 hover:underline text-sm font-medium">&larr; Back to Home</a>
        </div>
        
        <div class="text-center mb-12">
            <h1 class="text-4xl sm:text-5xl font-bold text-rose-800 dark:text-rose-400 mb-4">Chemistry MCQs (Examveda)</h1>
            <p class="text-lg text-gray-600 dark:text-gray-400">High-quality Chemistry MCQs for Sikkim PSC & Competitive Exams</p>
            <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">{sum(s['count'] for s in sections)} Questions</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
{cards_html}
        </div>
        
        <div class="text-center mt-12 text-sm text-gray-500 dark:text-gray-400">
            <p>Sikkim PSC Preparation Hub &copy; <span id="year"></span></p>
        </div>
    </div>
    
    <script>
        document.getElementById('year').textContent = new Date().getFullYear();
        
        // Dark mode detection
        if (localStorage.getItem('theme') === 'dark' || 
            (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.documentElement.classList.add('dark');
        }}
    </script>
</body>
</html>'''
    return html

def main():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chemistry_mcqs_scraped.json')
    if not os.path.exists(json_path):
        print(f"Scraped file not found at {json_path}!")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)
        
    print(f"Loaded {len(questions)} raw questions.")
    
    # Classification
    buckets = {cat: [] for cat in CATEGORIES}
    buckets["General Chemistry"] = []
    
    unique_questions = set()
    deduped_qs = []
    
    for q in questions:
        q_hash = re.sub(r'[^a-z0-9]', '', q['text'].lower())
        if q_hash in unique_questions:
            continue
        unique_questions.add(q_hash)
        deduped_qs.append(q)
        
        cat = classify_question(q['text'])
        buckets[cat].append(q)
        
    print(f"Unique questions: {len(deduped_qs)}")
    
    # Generate HTML files
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Chemistry')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    sections_info = []
    for cat, qs in buckets.items():
        if not qs: continue
        
        slug = re.sub(r'[^a-z0-9]', '_', cat.lower())
        filename = f"{slug}.html"
        
        html_content = generate_quiz_html(cat, qs, slug)
        
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated {cat}: {len(qs)} questions -> {filename}")
        sections_info.append({
            "title": cat,
            "count": len(qs),
            "filename": filename
        })
        
    # Generate Landing Page
    landing_html = generate_landing_page(sections_info)
    with open(os.path.join(output_dir, 'chemistry.html'), 'w', encoding='utf-8') as f:
        f.write(landing_html)
    print("Generated chemistry.html landing page.")

if __name__ == "__main__":
    main()
