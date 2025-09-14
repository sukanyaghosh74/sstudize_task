from fpdf import FPDF
from datetime import datetime

def clean_text_for_pdf(text):
    """Clean text to remove Unicode characters that can't be encoded in latin-1"""
    if not text:
        return ""
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '→': '->',
        '•': '-',
        '–': '-',
        '—': '-',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
        '°': 'deg',
        '×': 'x',
        '÷': '/',
        '±': '+/-',
        '≤': '<=',
        '≥': '>=',
        '≠': '!=',
        '∞': 'infinity',
        'α': 'alpha',
        'β': 'beta',
        'γ': 'gamma',
        'δ': 'delta',
        'ε': 'epsilon',
        'π': 'pi',
        'σ': 'sigma',
        'μ': 'mu',
        'λ': 'lambda',
        'θ': 'theta',
        'φ': 'phi',
        'ψ': 'psi',
        'ω': 'omega',
        '∑': 'sum',
        '∏': 'product',
        '∫': 'integral',
        '√': 'sqrt',
        '∆': 'delta',
        '∇': 'nabla',
        '∂': 'partial',
        'ℵ': 'aleph',
        'ℜ': 'Re',
        'ℑ': 'Im',
        'ℂ': 'C',
        'ℝ': 'R',
        'ℕ': 'N',
        'ℤ': 'Z',
        'ℚ': 'Q',
        '∈': 'in',
        '∉': 'not in',
        '⊂': 'subset',
        '⊃': 'superset',
        '∪': 'union',
        '∩': 'intersection',
        '∅': 'empty set',
        '∀': 'for all',
        '∃': 'exists',
        '∧': 'and',
        '∨': 'or',
        '¬': 'not',
        '⇒': '=>',
        '⇔': '<=>',
        '∴': 'therefore',
        '∵': 'because',
        '⊥': 'perpendicular',
        '∥': 'parallel',
        '∠': 'angle',
        '△': 'triangle',
        '□': 'square',
        '○': 'circle',
        '◇': 'diamond',
        '♠': 'spade',
        '♣': 'club',
        '♥': 'heart',
        '♦': 'diamond',
        '★': '*',
        '☆': '*',
        '☀': 'sun',
        '☁': 'cloud',
        '☂': 'umbrella',
        '☃': 'snowman',
        '☄': 'comet',
        '☎': 'phone',
        '☏': 'phone',
        '☐': 'checkbox',
        '☑': 'checked',
        '☒': 'crossed',
        '☓': 'cross',
        '☔': 'umbrella',
        '☕': 'coffee',
        '☖': 'dice',
        '☗': 'dice',
        '☘': 'clover',
        '☙': 'flower',
        '☚': 'left',
        '☛': 'right',
        '☜': 'left',
        '☝': 'up',
        '☞': 'right',
        '☟': 'down',
        '☠': 'skull',
        '☡': 'warning',
        '☢': 'radioactive',
        '☣': 'biohazard',
        '☤': 'caduceus',
        '☥': 'ankh',
        '☦': 'cross',
        '☧': 'cross',
        '☨': 'cross',
        '☩': 'cross',
        '☪': 'star',
        '☫': 'star',
        '☬': 'star',
        '☭': 'hammer',
        '☮': 'peace',
        '☯': 'yin yang',
        '☰': 'trigram',
        '☱': 'trigram',
        '☲': 'trigram',
        '☳': 'trigram',
        '☴': 'trigram',
        '☵': 'trigram',
        '☶': 'trigram',
        '☷': 'trigram',
        '☸': 'wheel',
        '☹': 'frown',
        '☺': 'smile',
        '☻': 'smile',
        '☼': 'sun',
        '☽': 'moon',
        '☾': 'moon',
        '☿': 'mercury',
        '♀': 'female',
        '♁': 'earth',
        '♂': 'male',
        '♃': 'jupiter',
        '♄': 'saturn',
        '♅': 'uranus',
        '♆': 'neptune',
        '♇': 'pluto',
        '♈': 'aries',
        '♉': 'taurus',
        '♊': 'gemini',
        '♋': 'cancer',
        '♌': 'leo',
        '♍': 'virgo',
        '♎': 'libra',
        '♏': 'scorpio',
        '♐': 'sagittarius',
        '♑': 'capricorn',
        '♒': 'aquarius',
        '♓': 'pisces',
        '♔': 'king',
        '♕': 'queen',
        '♖': 'rook',
        '♗': 'bishop',
        '♘': 'knight',
        '♙': 'pawn',
        '♚': 'king',
        '♛': 'queen',
        '♜': 'rook',
        '♝': 'bishop',
        '♞': 'knight',
        '♟': 'pawn',
        '♠': 'spade',
        '♡': 'heart',
        '♢': 'diamond',
        '♣': 'club',
        '♤': 'spade',
        '♥': 'heart',
        '♦': 'diamond',
        '♧': 'club',
        '♨': 'hot springs',
        '♩': 'note',
        '♪': 'note',
        '♫': 'notes',
        '♬': 'notes',
        '♭': 'flat',
        '♮': 'natural',
        '♯': 'sharp',
        '♰': 'cross',
        '♱': 'cross',
        '♲': 'recycle',
        '♳': 'recycle',
        '♴': 'recycle',
        '♵': 'recycle',
        '♶': 'recycle',
        '♷': 'recycle',
        '♸': 'recycle',
        '♹': 'recycle',
        '♺': 'recycle',
        '♻': 'recycle',
        '♼': 'recycle',
        '♽': 'recycle',
        '♾': 'recycle',
        '♿': 'wheelchair',
        '⚀': 'dice',
        '⚁': 'dice',
        '⚂': 'dice',
        '⚃': 'dice',
        '⚄': 'dice',
        '⚅': 'dice',
        '⚆': 'dice',
        '⚇': 'dice',
        '⚈': 'dice',
        '⚉': 'dice',
        '⚊': 'line',
        '⚋': 'line',
        '⚌': 'line',
        '⚍': 'line',
        '⚎': 'line',
        '⚏': 'line',
        '⚐': 'flag',
        '⚑': 'flag',
        '⚒': 'hammer',
        '⚓': 'anchor',
        '⚔': 'swords',
        '⚕': 'staff',
        '⚖': 'scales',
        '⚗': 'alembic',
        '⚘': 'flower',
        '⚙': 'gear',
        '⚚': 'staff',
        '⚛': 'atom',
        '⚜': 'fleur',
        '⚝': 'star',
        '⚞': 'star',
        '⚟': 'star',
        '⚠': 'warning',
        '⚡': 'lightning',
        '⚢': 'female',
        '⚣': 'male',
        '⚤': 'male',
        '⚥': 'male',
        '⚦': 'male',
        '⚧': 'male',
        '⚨': 'male',
        '⚩': 'male',
        '⚪': 'circle',
        '⚫': 'circle',
        '⚬': 'circle',
        '⚭': 'circle',
        '⚮': 'circle',
        '⚯': 'circle',
        '⚰': 'coffin',
        '⚱': 'urn',
        '⚲': 'male',
        '⚳': 'ceres',
        '⚴': 'pallas',
        '⚵': 'juno',
        '⚶': 'vesta',
        '⚷': 'chiron',
        '⚸': 'lilith',
        '⚹': 'sextile',
        '⚺': 'semisextile',
        '⚻': 'quincunx',
        '⚼': 'sesquiquadrate',
        '⚽': 'soccer',
        '⚾': 'baseball',
        '⚿': 'key',
        '⛀': 'white',
        '⛁': 'black',
        '⛂': 'white',
        '⛃': 'black',
        '⛄': 'snowman',
        '⛅': 'cloud',
        '⛆': 'rain',
        '⛇': 'snow',
        '⛈': 'storm',
        '⛉': 'umbrella',
        '⛊': 'hot',
        '⛋': 'cold',
        '⛌': 'no',
        '⛍': 'no',
        '⛎': 'ophiuchus',
        '⛏': 'pick',
        '⛐': 'no',
        '⛑': 'helmet',
        '⛒': 'chains',
        '⛓': 'chains',
        '⛔': 'no',
        '⛕': 'no',
        '⛖': 'no',
        '⛗': 'no',
        '⛘': 'no',
        '⛙': 'no',
        '⛚': 'no',
        '⛛': 'no',
        '⛜': 'no',
        '⛝': 'no',
        '⛞': 'no',
        '⛟': 'no',
        '⛠': 'no',
        '⛡': 'no',
        '⛢': 'uranus',
        '⛣': 'no',
        '⛤': 'no',
        '⛥': 'no',
        '⛦': 'no',
        '⛧': 'no',
        '⛨': 'no',
        '⛩': 'shrine',
        '⛪': 'church',
        '⛫': 'castle',
        '⛬': 'no',
        '⛭': 'no',
        '⛮': 'no',
        '⛯': 'no',
        '⛰': 'mountain',
        '⛱': 'umbrella',
        '⛲': 'fountain',
        '⛳': 'flag',
        '⛴': 'ferry',
        '⛵': 'sailboat',
        '⛶': 'no',
        '⛷': 'skier',
        '⛸': 'skate',
        '⛹': 'person',
        '⛺': 'tent',
        '⛻': 'no',
        '⛼': 'no',
        '⛽': 'fuel',
        '⛾': 'no',
        '⛿': 'no',
    }
    
    result = str(text)
    for unicode_char, ascii_replacement in replacements.items():
        result = result.replace(unicode_char, ascii_replacement)
    
    # Remove any remaining non-ASCII characters
    result = ''.join(char if ord(char) < 128 else '?' for char in result)
    return result

def generate_roadmap_pdf(student, roadmap, filename_or_buffer):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Title
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, clean_text_for_pdf("Personalized Study Roadmap"), ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_text_for_pdf(f"Student: {student.name} | Grade: {student.grade} | Age: {student.age}"), ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, clean_text_for_pdf(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), ln=True)
    pdf.cell(0, 6, clean_text_for_pdf(f"Duration: {roadmap.duration_weeks} weeks"), ln=True)
    pdf.ln(8)

    # Student Profile Summary
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, clean_text_for_pdf("Student Profile Summary"), ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, clean_text_for_pdf(f"Learning Style: {student.learning_style.title()}"), ln=True)
    pdf.cell(0, 6, clean_text_for_pdf(f"Available Study Hours/Day: {student.available_hours_per_day}"), ln=True)
    pdf.cell(0, 6, clean_text_for_pdf(f"Preferred Study Times: {', '.join(student.preferred_study_times)}"), ln=True)
    pdf.ln(5)

    # Current vs Target Scores
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_text_for_pdf("Current vs Target Scores:"), ln=True)
    pdf.set_font("Arial", size=9)
    for subject, current_score in student.current_scores.items():
        target_score = student.target_scores.get(subject, 0)
        improvement = target_score - current_score
        pdf.cell(0, 5, clean_text_for_pdf(f"{subject.value}: {current_score} -> {target_score} (Improvement: +{improvement})"), ln=True)
    pdf.ln(5)

    # Overall Goals
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, clean_text_for_pdf("Overall Goals:"), ln=True)
    pdf.set_font("Arial", size=10)
    for goal in getattr(roadmap, 'overall_goals', []):
        pdf.cell(0, 6, clean_text_for_pdf(f"- {goal}"), ln=True)
    pdf.ln(5)

    # Success Metrics
    if hasattr(roadmap, 'success_metrics') and roadmap.success_metrics:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, clean_text_for_pdf("Success Metrics:"), ln=True)
        pdf.set_font("Arial", size=9)
        for metric, value in roadmap.success_metrics.items():
            pdf.cell(0, 5, clean_text_for_pdf(f"- {metric}: {value}"), ln=True)
        pdf.ln(5)

    # Weekly Plans with Detailed Tasks
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, clean_text_for_pdf("Detailed Weekly Study Plans"), ln=True)
    pdf.ln(3)

    for week in getattr(roadmap, 'weekly_plans', []):
        # Check if we need a new page
        if pdf.get_y() > 250:
            pdf.add_page()
        
        pdf.set_font("Arial", "B", 12)
        week_title = f"Week {getattr(week, 'week_number', '?')}: {getattr(week, 'start_date', datetime.now()).strftime('%Y-%m-%d')} to {getattr(week, 'end_date', datetime.now()).strftime('%Y-%m-%d')}"
        pdf.cell(0, 8, clean_text_for_pdf(week_title), ln=True)
        
        # Week summary
        pdf.set_font("Arial", size=9)
        total_hours = getattr(week, 'total_hours', 0)
        pdf.cell(0, 5, clean_text_for_pdf(f"Total Study Hours: {total_hours}"), ln=True)
        
        # Subject breakdown
        subject_breakdown = getattr(week, 'subject_breakdown', {})
        if subject_breakdown:
            pdf.cell(0, 5, clean_text_for_pdf("Subject Breakdown:"), ln=True)
            for subject, hours in subject_breakdown.items():
                pdf.cell(0, 4, clean_text_for_pdf(f"  - {subject.value}: {hours} hours"), ln=True)
        pdf.ln(3)

        # Detailed Tasks
        tasks = getattr(week, 'tasks', [])
        if tasks:
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, clean_text_for_pdf("Study Tasks:"), ln=True)
            pdf.set_font("Arial", size=9)
            
            for i, task in enumerate(tasks, 1):
                # Check if we need a new page for this task
                if pdf.get_y() > 240:
                    pdf.add_page()
                
                # Task header
                subject_name = getattr(task.subject, 'value', str(task.subject)) if hasattr(task, 'subject') else 'Unknown'
                priority = getattr(task.priority, 'value', str(task.priority)) if hasattr(task, 'priority') else 'medium'
                due_date = getattr(task, 'due_date', datetime.now()).strftime('%Y-%m-%d')
                
                pdf.set_font("Arial", "B", 9)
                pdf.cell(0, 5, clean_text_for_pdf(f"{i}. {getattr(task, 'title', 'Untitled Task')}"), ln=True)
                pdf.set_font("Arial", size=8)
                pdf.cell(0, 4, clean_text_for_pdf(f"   Subject: {subject_name} | Priority: {priority.title()} | Due: {due_date}"), ln=True)
                
                # Task details
                if hasattr(task, 'description') and task.description:
                    pdf.cell(0, 4, clean_text_for_pdf(f"   Description: {task.description}"), ln=True)
                
                if hasattr(task, 'topic') and task.topic:
                    pdf.cell(0, 4, clean_text_for_pdf(f"   Topic: {task.topic}"), ln=True)
                
                if hasattr(task, 'estimated_duration'):
                    duration = task.estimated_duration
                    hours = duration // 60
                    minutes = duration % 60
                    if hours > 0:
                        pdf.cell(0, 4, clean_text_for_pdf(f"   Duration: {hours}h {minutes}m"), ln=True)
                    else:
                        pdf.cell(0, 4, clean_text_for_pdf(f"   Duration: {minutes} minutes"), ln=True)
                
                # Learning resources
                resources = getattr(task, 'resources', [])
                if resources:
                    pdf.cell(0, 4, clean_text_for_pdf(f"   Resources: {len(resources)} available"), ln=True)
                    for resource in resources[:2]:  # Show first 2 resources
                        pdf.cell(0, 3, clean_text_for_pdf(f"     - {getattr(resource, 'title', 'Resource')} ({getattr(resource, 'resource_type', 'unknown')})"), ln=True)
                    if len(resources) > 2:
                        pdf.cell(0, 3, clean_text_for_pdf(f"     ... and {len(resources) - 2} more resources"), ln=True)
                
                pdf.ln(2)
        
        pdf.ln(5)

    if hasattr(filename_or_buffer, 'write'):
        # For BytesIO buffer, use output(dest='S') to get string, then encode to bytes
        pdf_string = pdf.output(dest='S')
        pdf_bytes = pdf_string.encode('latin-1')  # PDF uses latin-1 encoding
        filename_or_buffer.write(pdf_bytes)
        filename_or_buffer.seek(0)
    else:
        # For file path string
        pdf.output(filename_or_buffer)
    return filename_or_buffer
