import json
import os
import re

# Topic configuration for Ecology
TOPICS = [
    {
        "name": "Ecology & Ecosystems",
        "slug": "ecology_ecosystems",
        "keywords": ["ecosystem", "food chain", "food web", "pyramid of energy", "abiotic", "biotic", "biosphere", "biome", "niche", "habitat", "symbiosis", "mutualism", "commensalism", "parasitism"],
        "icon": "globe-alt"
    },
    {
        "name": "Pollution & Control",
        "slug": "pollution_control",
        "keywords": ["pollution", "pollutant", "acid rain", "smog", "aerosol", "cfc", "greenhouse", "ozone", "e-waste", "toxic", "sludge", "sewage", "effluent", "particulate"],
        "icon": "exclamation-triangle"
    },
    {
        "name": "Biodiversity & Conservation",
        "slug": "biodiversity_conservation",
        "keywords": ["biodiversity", "conservation", "national park", "sanctuary", "wildlife", "endangered", "species", "extinct", "red data book", "wetland", "ramsar"],
        "icon": "bug-ant"
    },
    {
        "name": "Climate & Environment",
        "slug": "climate_environment",
        "keywords": ["climate", "global warming", "solar", "radiation", "atmosphere", "troposphere", "stratosphere", "infrared", "ultraviolet", "greenhouse effect", "temperature"],
        "icon": "sun"
    },
    {
        "name": "Natural Resources & Energy",
        "slug": "natural_resources_energy",
        "keywords": ["resource", "energy", "solar power", "wind power", "fossil fuel", "renewable", "hydroelectric", "soil", "water", "hydrogen"],
        "icon": "bolt"
    }
]

def classify_question(text):
    text = text.lower()
    for topic in TOPICS:
        for keyword in topic["keywords"]:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                return topic["name"]
    return "Others"

def generate_quiz_html(title, questions, slug):
    """Generate a quiz HTML page."""
    
    quiz_data_items = []
    for q in questions:
        # Sanitize text for JS
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
        .options-list.answered {{
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
        <a href="ecology.html" class="back-link">&larr; Back to Ecology Topics</a>
        <h1 class="text-3xl font-bold text-green-800 dark:text-green-400 mb-2">{title}</h1>
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
            questionText.innerHTML = `<span class="text-green-600 dark:text-green-500 mr-2">Q${{index + 1}}.</span> ${{item.question}}`;
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
    """Generate landing page with neomorphic cards."""
    cards_html = ""
    colors = [
        ("green", "600"), ("emerald", "600"), ("teal", "600"), ("cyan", "600"),
        ("sky", "600"), ("blue", "600"), ("indigo", "600"), ("violet", "600"),
    ]
    
    # Map icons to SVG paths
    icons_svg = {
        "globe-alt": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A12.042 12.042 0 0112 17.25c-2.992 0-5.727-1.1-7.824-2.897m0 0A8.96 8.96 0 013 12c0-.773.098-1.523.282-2.238" />',
        "exclamation-triangle": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />',
        "bug-ant": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 2a1 1 0 011 1v1.1c1.9.3 3.5 1.5 4.3 3.2.3.6.5 1.4.5 2.2v2.5a6 6 0 001.2 3.6l.8 1.2a1 1 0 01-1.6 1.1l-.8-1.2A8 8 0 0116 12V9.5a4 4 0 00-.4-1.8c-.5-1.1-1.6-2-2.9-2.2V3a1 1 0 00-1-1zm0 20a1 1 0 01-1-1v-1.1c-1.9-.3-3.5-1.5-4.3-3.2-.3-.6-.5-1.4-.5-2.2v-2.5a6 6 0 00-1.2-3.6l-.8-1.2a1 1 0 011.6-1.1l.8 1.2a8 8 0 011.4 3.7V14.5c0 .8.2 1.6.6 2.3 1.1 2.1 3.2 3.5 5.7 3.7V21a1 1 0 01-1 1z" />', # Simplified
        "sun": '<path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-6.364-.386l1.591-1.591M3 12h2.25m.386-6.364l1.591 1.591M12 18.75V21m-6.364-.386l1.591-1.591M3 12h2.25m.386-6.364l1.591 1.591M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />',
        "bolt": '<path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />'
    }

    for i, sec in enumerate(sections):
        color = colors[i % len(colors)][0]
        title = sec['title']
        count = sec['count']
        filename = sec['filename']
        icon_slug = sec.get('icon', 'globe-alt')
        svg_path = icons_svg.get(icon_slug, icons_svg['globe-alt'])
        
        cards_html += f'''
                    <!-- {title} -->
                    <a href="{filename}"
                        class="quiz-card group block p-6 sm:p-8 fade-in-up focus:outline-none focus:ring-4 focus:ring-{color}-500/50">
                        <div class="flex flex-col items-center">
                            <div class="icon-bg mb-4 p-3 rounded-full group-hover:scale-110 transition-transform duration-300 bg-{color}-100 dark:bg-{color}-900/30">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="1.5" stroke="currentColor"
                                    class="w-8 h-8 text-{color}-600">
                                    {svg_path}
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ecology MCQs | Sikkim PSC Hub</title>
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
            <a href="../index.html" class="text-green-600 dark:text-green-400 hover:underline text-sm font-medium">&larr; Back to Home</a>
        </div>
        
        <div class="text-center mb-12">
            <h1 class="text-4xl sm:text-5xl font-bold text-green-800 dark:text-green-400 mb-4">Environmental Science & Ecology</h1>
            <p class="text-lg text-gray-600 dark:text-gray-400">Essential MCQs for Sikkim PSC & Competitive Exams</p>
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
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecology_mcqs_scraped.json')
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    print(f"Loaded {len(raw_data)} raw questions.")

    # Deduplicate
    unique_questions = set()
    deduped_qs = []
    
    for q in raw_data:
        # Simple normalization for hash
        q_hash = re.sub(r'[^a-z0-9]', '', q['text'].lower())
        if q_hash in unique_questions:
            continue
        unique_questions.add(q_hash)
        deduped_qs.append(q)
    
    print(f"Unique questions: {len(deduped_qs)}")

    # Classify
    buckets = {topic['name']: [] for topic in TOPICS}
    buckets["Others"] = []
    
    for q in deduped_qs:
        topic = classify_question(q['text'])
        buckets[topic].append(q)

    # Generate HTML files
    sections_info = []
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Ecology')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for topic_name, qs in buckets.items():
        if not qs: continue
        if topic_name == "Others" and len(qs) < 5: continue
        
        # Get topic config for icon/slug
        topic_config = next((t for t in TOPICS if t['name'] == topic_name), {"slug": "others", "icon": "globe-alt"})
        slug = topic_config['slug']
        filename = f"{slug}.html"
        
        html_content = generate_quiz_html(topic_name, qs, slug)
        
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated {topic_name}: {len(qs)} questions -> {filename}")
        sections_info.append({
            "title": topic_name,
            "count": len(qs),
            "filename": filename,
            "icon": topic_config['icon']
        })

    # Generate Landing Page
    landing_html = generate_landing_page(sections_info)
    with open(os.path.join(output_dir, 'ecology.html'), 'w', encoding='utf-8') as f:
        f.write(landing_html)
    print("Generated ecology.html landing page.")

if __name__ == "__main__":
    main()
