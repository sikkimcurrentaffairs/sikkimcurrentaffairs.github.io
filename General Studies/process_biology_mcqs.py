import json
import os
import re

# ============================================================
# Classification Logic
# ============================================================
CATEGORIES = {
    "Botany": [
        "plant", "root", "stem", "leaf", "leaves", "flower", "seed", "fruit", 
        "photosynthesis", "chlorophyll", "chloroplast", "xylem", "phloem", 
        "angiosperm", "gymnosperm", "monocot", "dicot", "stamen", "pistil", 
        "pollen", "pollination", "germination", "botany", "algae", "fungi", 
        "bryophyte", "pteridophyte", "lichen", "auxin", "gibberellin", 
        "cytokinin", "stomata", "transpiration", "vegetative", "inflorescence"
    ],
    "Zoology": [
        "animal", "mammal", "bird", "reptile", "amphibian", "fish", "insect", 
        "arthropod", "mollusc", "porifera", "coelenterata", "annelida", 
        "echinodermata", "chordata", "vertebrate", "invertebrate", "cockroach", 
        "frog", "earthworm", "zoology", "larva", "pupa", "metamorphosis"
    ],
    "Cell Biology, Genetics & Evolution": [
        "cell", "nucleus", "dna", "rna", "chromosome", "gene", "genetics", 
        "mendel", "inheritance", "mutation", "ribosome", "mitochondria", 
        "golgi", "endoplasmic", "lysosome", "mitosis", "meiosis", "cytokinesis", 
        "replication", "transcription", "translation", "cytoplasm", "protoplasm",
        "allele", "genotype", "phenotype", "nucleic acid", "nucleotide",
        "evolution", "darwin", "lamarck", "selection", "species", "fossil", 
        "origin of life", "homologous", "analogous", "vestigial", "adaptation"
    ],
    "Human Physiology & Health": [
        "human", "body", "heart", "blood", "lung", "breathe", "respiration",
        "kidney", "excretion", "urine", "brain", "nerve", "neuron", "eye", 
        "ear", "muscle", "bone", "skeleton", "joint", "endocrine", "hormone", 
        "gland", "digest", "stomach", "intestine", "liver", "pancreas", "bile",
        "vitamin", "nutrient", "nutrition", "deficiency", "disease", "syndrome", 
        "immunity", "antibody", "antigen", "vaccine", "virus", "bacteria", 
        "infection", "pathogen", "disorder", "symptom", "blood group"
    ],
    "Ecology & Environment": [
        "ecology", "ecosystem", "environment", "pollution", "pollutant",
        "biodiversity", "conservation", "ozone", "greenhouse", "global warming", 
        "food chain", "food web", "producer", "consumer", "decomposer", 
        "symbiosis", "parasite", "population", "community", "biosphere", 
        "habitat", "niche", "biomagnification", "acid rain"
    ],
    "Biotechnology & Biochemistry": [
        "biotechnology", "clone", "cloning", "genetic engineering", "transgenic",
        "enzyme", "protein", "carbohydrate", "lipid", "fat", "amino acid", 
        "metabolism", "fermentation", "catalyst", "biochemistry", "vitamin"
    ]
}

def classify_question(text):
    text_lower = text.lower()
    
    # Check each category
    scores = {cat: 0 for cat in CATEGORIES}
    
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            # Simple word boundary check to avoid substrings (e.g. "he" in "the")
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                scores[cat] += 1
            elif kw in text_lower: # broader match
                scores[cat] += 0.5
                
    # Find max score
    best_cat = "General Biology"
    max_score = 0.5 # Minimum threshold
    
    for cat, score in scores.items():
        if score > max_score:
            max_score = score
            best_cat = cat
            
    return best_cat

# ============================================================
# HTML Generation
# ============================================================
def generate_quiz_html(title, questions, slug):
    """Generate a quiz HTML page."""
    
    quiz_data_items = []
    for q in questions:
        q_text = q['text'].replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        
        opts = []
        for letter in ['A', 'B', 'C', 'D']:
            opt_text = q['options'].get(letter, '')
            opt_text = opt_text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
            opts.append(opt_text)
            
        answer_idx = ord(q['answer']) - ord('A')
        if answer_idx < 0 or answer_idx > 3: answer_idx = 0 # Safety
        
        quiz_data_items.append(f'''            {{
                question: "{q_text}",
                options: ["{opts[0]}", "{opts[1]}", "{opts[2]}", "{opts[3]}"],
                answer: {answer_idx}
            }}''')
            
    quiz_data_js = ',\n'.join(quiz_data_items)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Sikkim PSC Hub</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f4f7f9;
            color: #333;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}
        #quiz-container {{
            max-width: 800px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #0056b3;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 15px;
            color: #0056b3;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        .question-block {{
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .question-text {{
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .options-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .option {{
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s, border-color 0.3s;
        }}
        .option:hover {{
            background-color: #e9ecef;
            border-color: #bbb;
        }}
        .option.correct {{
            background-color: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
            font-weight: bold;
        }}
        .option.incorrect {{
            background-color: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
            font-weight: bold;
        }}
        .options-list.answered .option:not(.correct):not(.incorrect) {{
            opacity: 0.7;
        }}
        .options-list.answered .option {{
            cursor: default;
            pointer-events: none;
        }}
        .quiz-stats {{
            text-align: center;
            margin-bottom: 20px;
            color: #666;
            font-size: 0.95em;
        }}
    </style>
</head>
<body>

    <div id="quiz-container">
        <a href="biology.html" class="back-link">&larr; Back to Biology</a>
        <h1>{title}</h1>
        <p class="quiz-stats">{len(questions)} Questions</p>
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
            questionText.textContent = `${{index + 1}}) ${{item.question}}`;
            questionBlock.appendChild(questionText);

            const optionsList = document.createElement('ul');
            optionsList.className = 'options-list';

            item.options.forEach((option, optionIndex) => {{
                const optionItem = document.createElement('li');
                optionItem.className = 'option';
                optionItem.textContent = option;
                optionItem.dataset.index = optionIndex;

                optionItem.addEventListener('click', () => {{
                    if (optionsList.classList.contains('answered')) {{
                        return;
                    }}
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
    </script>
</body>
</html>'''
    return html

def generate_landing_page(sections):
    """Generate landing page cards."""
    cards_html = ""
    colors = [
        ("lime", "600"), ("green", "600"), ("emerald", "600"), ("teal", "600"),
        ("cyan", "600"), ("sky", "600"), ("blue", "600"), ("indigo", "600"),
        ("violet", "600"), ("purple", "600"), ("fuchsia", "600"), ("pink", "600"),
        ("rose", "600"), ("amber", "600"), ("orange", "600"),
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
                                        d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                                </svg>
                            </div>
                            <h2 class="text-xl sm:text-2xl font-semibold text-center mb-2 group-hover:text-{color}-600 dark:group-hover:text-{color}-400 transition-colors duration-300">
                                {title}</h2>
                            <p class="text-sm text-center mb-4 text-gray-500">{count} Questions</p>
                            <span class="inline-flex items-center justify-center px-5 py-2.5 text-sm font-medium text-white bg-{color}-600 rounded-lg group-hover:bg-{color}-700 transition-all duration-300 transform group-hover:scale-105 shadow-md">
                                Start Quiz
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
    <title>Biology MCQs | Sikkim PSC Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                    }}
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
            <h1 class="text-4xl sm:text-5xl font-bold text-sky-800 dark:text-sky-300 mb-4">Biology MCQs (Examveda)</h1>
            <p class="text-lg text-gray-600 dark:text-gray-400">Comprehensive Biology MCQs for Sikkim PSC & Competitive Exams</p>
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

# ============================================================
# Main Execution
# ============================================================
def main():
    if not os.path.exists('biology_mcqs_scraped.json'):
        print("Scraped file not found!")
        return

    with open('biology_mcqs_scraped.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
        
    print(f"Loaded {len(questions)} raw questions.")
    
    # Classification
    buckets = {cat: [] for cat in CATEGORIES}
    buckets["General Biology"] = []
    
    unique_questions = set()
    
    for q in questions:
        q_text = q['text'].strip()
        # Deduplication
        if q_text in unique_questions:
            continue
        unique_questions.add(q_text)
        
        category = classify_question(q_text)
        buckets[category].append(q)
        
    # Output Directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Biology')
    os.makedirs(output_dir, exist_ok=True)
    
    sections_meta = []
    
    for cat, qs in buckets.items():
        if not qs: continue
        
        filename = re.sub(r'[^a-z0-9]+', '_', cat.lower()).strip('_') + ".html"
        filepath = os.path.join(output_dir, filename)
        
        html = generate_quiz_html(cat, qs, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"Generated {cat}: {len(qs)} questions -> {filename}")
        
        sections_meta.append({
            'title': cat,
            'filename': filename,
            'count': len(qs)
        })
        
    # Landing Page
    landing_html = generate_landing_page(sections_meta)
    with open(os.path.join(output_dir, 'biology.html'), 'w', encoding='utf-8') as f:
        f.write(landing_html)
        
    print("Generated biology.html landing page.")

if __name__ == "__main__":
    main()
