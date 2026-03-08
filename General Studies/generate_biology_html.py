"""
Biology MCQ HTML Generator
Reads biology_mcqs.json and generates individual quiz HTML files
plus a Biology landing page.
"""
import json
import os
import re

# Read extracted MCQs
with open('biology_mcqs.json', 'r', encoding='utf-8') as f:
    sections = json.load(f)

# Create output directory
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Biology')
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory: {os.path.abspath(output_dir)}")

# ============================================================
# HTML Template for quiz pages (matches quiz1.html style)
# ============================================================
def generate_quiz_html(title, questions):
    """Generate a quiz HTML page matching the existing template."""
    
    # Build quizData JavaScript array
    quiz_data_items = []
    for q in questions:
        # Clean the question text
        q_text = q['text'].strip()
        # Remove leading/trailing noise
        q_text = re.sub(r'^[~\-:*\.]+\s*', '', q_text)
        q_text = re.sub(r'[~\-:*]+$', '', q_text).strip()
        # Escape quotes for JavaScript
        q_text = q_text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        
        # Get options in order a, b, c, d
        opts = []
        for letter in ['a', 'b', 'c', 'd']:
            opt_text = q['options'].get(letter, '')
            opt_text = re.sub(r'^[~\-:*\.]+\s*', '', opt_text)
            opt_text = re.sub(r'[~\-:*]+$', '', opt_text).strip()
            opt_text = opt_text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
            opts.append(opt_text)
        
        # Convert answer letter to index (a=0, b=1, c=2, d=3)
        answer_idx = ord(q['answer']) - ord('a')
        
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
    <title>Biology - {title} | Sikkim PSC Hub</title>
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
        <!-- Questions will be dynamically inserted here by JavaScript -->
    </div>

    <script>
        const quizData = [
{quiz_data_js}
        ];

        const quizContainer = document.getElementById('quiz-container');

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
            quizContainer.appendChild(questionBlock);
        }});
    </script>
</body>
</html>'''
    
    return html

# ============================================================
# Generate quiz HTML files for each section
# ============================================================
section_files = []

for sec in sections:
    title = sec['title']
    questions = sec['questions']
    slug = sec['slug']
    
    if len(questions) == 0:
        print(f"Skipping {title} (0 questions)")
        continue
    
    filename = f"{slug}.html"
    filepath = os.path.join(output_dir, filename)
    
    html = generate_quiz_html(title, questions)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    section_files.append({
        'title': title,
        'filename': filename,
        'count': len(questions)
    })
    
    print(f"Generated: {filename} ({len(questions)} questions)")

# ============================================================
# Generate Biology landing page
# ============================================================
def generate_landing_page(section_files):
    """Generate the Biology landing page with links to all sections."""
    
    cards_html = ""
    colors = [
        ("lime", "600"), ("green", "600"), ("emerald", "600"), ("teal", "600"),
        ("cyan", "600"), ("sky", "600"), ("blue", "600"), ("indigo", "600"),
        ("violet", "600"), ("purple", "600"), ("fuchsia", "600"), ("pink", "600"),
        ("rose", "600"), ("amber", "600"), ("orange", "600"),
    ]
    
    for i, sf in enumerate(section_files):
        color = colors[i % len(colors)][0]
        cards_html += f'''
                    <!-- {sf['title']} -->
                    <a href="{sf['filename']}"
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
                                {sf['title']}</h2>
                            <p class="text-sm text-center mb-4 text-gray-500">{sf['count']} Questions</p>
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
            <h1 class="text-4xl sm:text-5xl font-bold text-sky-800 dark:text-sky-300 mb-4">Biology MCQs</h1>
            <p class="text-lg text-gray-600 dark:text-gray-400">Comprehensive Biology MCQs for Sikkim PSC & Competitive Exams</p>
            <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">{sum(sf['count'] for sf in section_files)} Questions across {len(section_files)} Topics</p>
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

landing_html = generate_landing_page(section_files)
landing_path = os.path.join(output_dir, 'biology.html')
with open(landing_path, 'w', encoding='utf-8') as f:
    f.write(landing_html)

print(f"\nGenerated landing page: biology.html")
print(f"\nAll files saved to: {os.path.abspath(output_dir)}")
print(f"Total: {len(section_files)} quiz files + 1 landing page")
