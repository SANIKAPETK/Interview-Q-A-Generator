import streamlit as st
import fitz
from google import genai
from datetime import datetime
from fpdf import FPDF
import time
import hashlib

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Interview Q&A Generator",
    layout="centered"
)

# ---------------- Reset ID (for widget re-render) ----------------
if "reset_id" not in st.session_state:
    st.session_state["reset_id"] = 0

# ---------------- Session History Initialization ----------------
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# ---------------- API Rate Limiting ----------------
if "last_api_call" not in st.session_state:
    st.session_state["last_api_call"] = 0

if "api_cache" not in st.session_state:
    st.session_state["api_cache"] = {}

# ---------------- Clear Form Logic ----------------
def clear_form():
    for key in list(st.session_state.keys()):
        if key not in ["reset_id", "conversation_history", "last_api_call", "api_cache"]:
            del st.session_state[key]

def clear_and_reset():
    clear_form()
    st.session_state["reset_id"] += 1

def clear_history():
    st.session_state["conversation_history"] = []
    st.success("Conversation history cleared!")

# ---------------- Rate Limiting Helper ----------------
def can_make_api_call():
    """Enforce minimum 5 seconds between API calls"""
    current_time = time.time()
    time_since_last = current_time - st.session_state["last_api_call"]
    
    if time_since_last < 5:
        return False, 5 - time_since_last
    return True, 0

def get_cache_key(text):
    """Generate cache key for API responses"""
    return hashlib.md5(text.encode()).hexdigest()

# ---------------- API Call with Retry ----------------
def call_gemini_with_retry(client, model, prompt, max_retries=4, cache_key=None):
    """Call Gemini API with exponential backoff retry logic and caching"""
    
    # Check cache first
    if cache_key and cache_key in st.session_state["api_cache"]:
        st.success("✅ Using cached response (no API call needed)")
        return st.session_state["api_cache"][cache_key]
    
    for attempt in range(max_retries):
        try:
            # Add initial delay to avoid immediate rate limits
            if attempt == 0:
                time.sleep(1)  # 1 second delay before first attempt
            
            response = client.models.generate_content(
                model=model,
                contents=[{"text": prompt}]
            )
            result = response.text
            
            # Cache the result
            if cache_key:
                st.session_state["api_cache"][cache_key] = result
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle 503 Server Overload
            if "503" in error_msg or "overloaded" in error_msg.lower() or "unavailable" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 3  # 3, 6, 12, 24 seconds
                    st.warning(f"⏳ Server overloaded. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    
                    # Show countdown
                    progress_bar = st.progress(0)
                    for i in range(wait_time):
                        progress_bar.progress((i + 1) / wait_time)
                        time.sleep(1)
                    progress_bar.empty()
                else:
                    st.error(f"❌ Server still overloaded after {max_retries} attempts. Please try again in a few minutes.")
                    st.info("💡 The model might be experiencing high demand. Try switching to gemini-1.5-flash if this persists.")
                    raise e
            
            # Handle 429 Rate Limit
            elif "429" in error_msg:
                if attempt == 0:
                    st.error("❌ **Rate limit hit on first attempt!**")
                    st.warning("""
                    **Possible causes:**
                    - You've exceeded your free tier quota (15 requests/min or 1500/day)
                    - API quota was already exhausted from previous usage
                    
                    **Solutions:**
                    1. Wait 60 seconds and try again
                    2. Check your quota at: https://aistudio.google.com/app/apikey
                    """)
                
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5  # 5, 10, 20, 40 seconds
                    st.warning(f"⏳ Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    
                    progress_bar = st.progress(0)
                    for i in range(wait_time):
                        progress_bar.progress((i + 1) / wait_time)
                        time.sleep(1)
                    progress_bar.empty()
                else:
                    st.error(f"❌ Failed after {max_retries} attempts. Please wait 1-2 minutes before trying again.")
                    raise e
            
            # Handle other errors
            elif attempt < max_retries - 1:
                wait_time = 2
                st.warning(f"⚠️ Request failed: {error_msg}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                st.error(f"❌ Error after {max_retries} attempts: {error_msg}")
                raise e
    
    return None

# ---------------- Export Functions ----------------
def export_to_text():
    """Export conversation history to text format"""
    if not st.session_state["conversation_history"]:
        return None
    
    content = "=" * 80 + "\n"
    content += "INTERVIEW Q&A SESSION HISTORY\n"
    content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += "=" * 80 + "\n\n"
    
    for idx, entry in enumerate(st.session_state["conversation_history"], 1):
        content += f"\n{'=' * 80}\n"
        content += f"SESSION {idx}\n"
        content += f"Timestamp: {entry['timestamp']}\n"
        content += f"{'=' * 80}\n\n"
        
        content += f"JOB ROLE/JD:\n{entry['job_or_jd']}\n\n"
        
        if entry.get('document_summary'):
            content += f"DOCUMENT SUMMARY:\n{entry['document_summary']}\n\n"
        
        content += f"SETTINGS:\n"
        content += f"- Category: {entry['category']}\n"
        content += f"- Difficulty: {entry['difficulty']}\n"
        content += f"- Experience Level: {entry['experience_level']}\n\n"
        
        content += f"GENERATED Q&A:\n{entry['qas']}\n\n"
        
        if entry.get('evaluations'):
            content += "ANSWER EVALUATIONS:\n"
            for eval_idx, evaluation in enumerate(entry['evaluations'], 1):
                content += f"\nEvaluation {eval_idx}:\n"
                content += f"Question: {evaluation['question']}\n"
                content += f"User Answer: {evaluation['user_answer']}\n"
                content += f"Feedback:\n{evaluation['feedback']}\n\n"
    
    return content

def export_to_pdf():
    """Export conversation history to PDF format with encoding safety"""
    if not st.session_state["conversation_history"]:
        return None
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def clean_text(text):
        if not isinstance(text, str):
            return str(text)
        replacements = {
            '\u2013': '-',
            '\u2014': '-',
            '\u2018': "'",
            '\u2019': "'",
            '\u201c': '"',
            '\u201d': '"',
            '\u2022': '*',
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, "Interview Q&A Session History", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)
    
    for idx, entry in enumerate(st.session_state["conversation_history"], 1):
        pdf.add_page()
        
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Session {idx}", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Timestamp: {entry['timestamp']}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Job Role/JD:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, clean_text(entry['job_or_jd']))
        pdf.ln(3)
        
        if entry.get('document_summary'):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Document Summary:", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 6, clean_text(entry['document_summary']))
            pdf.ln(3)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Settings:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, clean_text(f"Category: {entry['category']}, Difficulty: {entry['difficulty']}, Experience: {entry['experience_level']}"), ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Generated Q&A:", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, clean_text(entry['qas']))
        pdf.ln(3)
        
        if entry.get('evaluations'):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Answer Evaluations:", ln=True)
            for eval_idx, evaluation in enumerate(entry['evaluations'], 1):
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, f"Evaluation {eval_idx}:", ln=True)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, clean_text(f"Question: {evaluation['question']}"))
                pdf.multi_cell(0, 5, clean_text(f"User Answer: {evaluation['user_answer']}"))
                pdf.multi_cell(0, 5, clean_text(f"Feedback: {evaluation['feedback']}"))
                pdf.ln(2)
    
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ---------------- Lavender UI ----------------
st.markdown("""
<style>
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background-color: #E6E6FA;
}
.main-container {
    background-color: #ffffff;
    padding: 1rem 2rem 2rem 2rem;
    border-radius: 1.5rem;
    box-shadow: 0 10px 15px rgba(0,0,0,0.1);
}
.stButton > button {
    background-color: #8A2BE2;
    color: white;
    font-weight: 600;
    padding: 0.7rem 2rem;
    border-radius: 0.5rem;
    border: none;
}
.stButton > button:hover {
    background-color: #6A0DAD;
}
.stButton > button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}
.history-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #8A2BE2;
}
</style>
""", unsafe_allow_html=True)

st.title("Interview Q&A Generator")

# ---------------- Info Banner ----------------
st.info("💡 **Using Gemini 2.5 Flash:** Wait at least 5 seconds between requests. The app automatically handles server issues with smart retries.")

# ---------------- Gemini Client ----------------
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"❌ Failed to initialize Gemini API: {e}")
    st.stop()

# ---------------- Helper Functions ----------------
def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF with size limits"""
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    
    # Only process first 3 pages to reduce token usage
    max_pages = min(3, len(pdf))
    for page_num in range(max_pages):
        text += pdf[page_num].get_text()
    
    # Hard limit on characters (approximately 1000 tokens)
    if len(text) > 4000:
        text = text[:4000] + "\n\n[Document truncated for processing...]"
    
    return text


def generate_document_summary(document_text):
    """Generate document summary with caching"""
    
    # Additional safety truncation
    if len(document_text) > 3500:
        document_text = document_text[:3500] + "\n[Content truncated]"
    
    prompt = f"""
You are an expert document analyzer. Analyze the provided document and determine if it's a RESUME or JOB DESCRIPTION, then generate an appropriate summary.

IF IT'S A RESUME:
Generate a concise, single-paragraph professional summary including:
1. Full name (in bold)
2. Educational background (degree, institution, graduation year, GPA/CGPA/percentage)
3. Core technical skills (programming languages, frameworks, libraries, tools, platforms, specialized domains)
4. Professional experience (company/organization names, duration, key responsibilities and achievements)
5. Major projects (project names with technologies used and key outcomes)
6. Certifications (list all certifications with issuing organization if mentioned)
7. Publications/Research (if any - title, journal/conference, date)
8. Contact information (email, phone, location)

Output format: **[Name]** is a [Degree] graduate ([Years], [GPA]) from [Institution] with expertise in [Skills]. [He/She] completed [Experience details with dates and achievements]. Key projects include [Project names with technologies]. [He/She] holds certifications in [Certifications list] and published [Publication details if any]. Contact: [Email, Phone, Location].

IF IT'S A JOB DESCRIPTION:
Generate a concise, single-paragraph summary including:
1. Job title/position (in bold)
2. Company name (if mentioned)
3. Key responsibilities and duties
4. Required technical skills and qualifications
5. Experience level required
6. Preferred qualifications or nice-to-haves
7. Work location/type (remote, hybrid, onsite)

Output format: **[Job Title]** at [Company] requires [Experience level] with expertise in [Required skills]. Key responsibilities include [Main duties]. Candidates should have [Qualifications and requirements]. Preferred qualifications include [Nice-to-haves]. Location: [Work type/location].

FORMATTING REQUIREMENTS:
- Output must be a SINGLE, well-structured paragraph
- Start with the key identifier (name for resume, job title for JD) in **bold** markdown format
- Be precise and concise - eliminate unnecessary words
- Include specific technical terms, tool names, and keywords exactly as mentioned
- Use commas and brief phrases to separate items within categories
- Maintain professional tone throughout
- Ensure EVERY important detail is captured without omission

Now analyze the following document and provide the appropriate summary:

{document_text}
"""
    
    cache_key = get_cache_key(f"summary_{document_text}")
    
    return call_gemini_with_retry(
        client,
        "gemini-2.5-flash",
        prompt,
        cache_key=cache_key
    )


def generate_qas(job_or_jd, summary_text, category, difficulty, experience_level):
    """Generate Q&A with caching"""
    prompt = f"""
You are a professional interview coach.

Generate exactly 4 interview questions WITH answers.

Strictly follow:
- Category: {category}
- Difficulty: {difficulty}
- Experience Level: {experience_level}

Context:
Job Role / JD:
{job_or_jd}

Resume Summary:
{summary_text}

Use numbered markdown.
No intro or conclusion.
"""
    
    cache_key = get_cache_key(f"qas_{job_or_jd}_{summary_text}_{category}_{difficulty}_{experience_level}")
    
    return call_gemini_with_retry(
        client,
        "gemini-2.5-flash",
        prompt,
        cache_key=cache_key
    )


def evaluate_answer(question, user_answer):
    """Evaluate answer with retry logic"""
    prompt = f"""
You are an interview evaluator.

Evaluate based on:
1. Completeness
2. Technical Accuracy
3. Communication Clarity

Provide:
- Score /10
- Feedback
- Improvements

Question:
{question}

Answer:
{user_answer}
"""
    
    return call_gemini_with_retry(
        client,
        "gemini-2.5-flash",
        prompt
    )

# ---------------- Sidebar for History ----------------
with st.sidebar:
    st.header("📜 Session History")
    
    if st.session_state["conversation_history"]:
        st.write(f"**Total Sessions:** {len(st.session_state['conversation_history'])}")
        
        st.subheader("Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            text_content = export_to_text()
            if text_content:
                st.download_button(
                    label="📄 Text",
                    data=text_content,
                    file_name=f"interview_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col2:
            pdf_content = export_to_pdf()
            if pdf_content:
                st.download_button(
                    label="📕 PDF",
                    data=pdf_content,
                    file_name=f"interview_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
        
        st.button("🗑️ Clear History", on_click=clear_history)
        st.divider()
        
        st.subheader("Previous Sessions")
        for idx, entry in enumerate(reversed(st.session_state["conversation_history"]), 1):
            with st.expander(f"Session {len(st.session_state['conversation_history']) - idx + 1} - {entry['timestamp']}"):
                st.write(f"**Category:** {entry['category']}")
                st.write(f"**Difficulty:** {entry['difficulty']}")
                st.write(f"**Experience:** {entry['experience_level']}")
                if st.button(f"Load Session", key=f"load_{idx}"):
                    st.session_state["loaded_session"] = entry
                    st.rerun()
    else:
        st.info("No session history yet. Generate Q&A to start!")

# ---------------- UI ----------------
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Load session if requested
    if "loaded_session" in st.session_state:
        loaded = st.session_state["loaded_session"]
        st.info(f"📂 Loaded session from {loaded['timestamp']}")
        
        st.markdown("### 📄 Loaded Session Details")
        st.markdown(f"**Job Role/JD:** {loaded['job_or_jd']}")
        if loaded.get('document_summary'):
            st.markdown(f"**Document Summary:** {loaded['document_summary']}")
        st.markdown(f"**Settings:** Category: {loaded['category']}, Difficulty: {loaded['difficulty']}, Experience: {loaded['experience_level']}")
        st.markdown("### Generated Q&A")
        st.markdown(loaded['qas'])
        
        if loaded.get('evaluations'):
            st.markdown("### Previous Evaluations")
            for eval_idx, evaluation in enumerate(loaded['evaluations'], 1):
                st.markdown(f"**Evaluation {eval_idx}:**")
                st.markdown(f"*Question:* {evaluation['question']}")
                st.markdown(f"*Your Answer:* {evaluation['user_answer']}")
                st.markdown(f"*Feedback:*\n{evaluation['feedback']}")
        
        if st.button("Close Loaded Session"):
            del st.session_state["loaded_session"]
            st.rerun()
        
        st.divider()

    # Job role / JD
    st.markdown("### Enter Job Role or Paste Job Description")
    job_or_jd = st.text_area(
        "Job Role / Job Description",
        placeholder="e.g. Software Engineer or paste full JD",
        height=100,
        key=f"job_or_jd_{st.session_state['reset_id']}"
    )

    # PDF upload
    st.markdown("### Upload Resume / JD (PDF)")
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key=f"uploaded_pdf_{st.session_state['reset_id']}"
    )

    summary_text = ""

    if uploaded_file is not None:
        # Check cache first
        file_hash = get_cache_key(uploaded_file.name + str(uploaded_file.size))
        cache_key = f"pdf_summary_{file_hash}"
        
        if cache_key in st.session_state["api_cache"]:
            summary_text = st.session_state["api_cache"][cache_key]
            st.session_state["summary_text"] = summary_text
            st.markdown("### 📄 Document Summary")
            st.markdown(summary_text)
        else:
            with st.spinner("Analyzing document..."):
                full_text = extract_text_from_pdf(uploaded_file)
                summary_text = generate_document_summary(full_text)
                st.session_state["summary_text"] = summary_text
                st.session_state["api_cache"][cache_key] = summary_text

            st.markdown("### 📄 Document Summary")
            st.markdown(summary_text)

    # Customize Interview Questions
    st.markdown("### 🎯 Customize Interview Questions")

    col1, col2, col3 = st.columns(3)

    with col1:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            key=f"difficulty_{st.session_state['reset_id']}"
        )

    with col2:
        category = st.selectbox(
            "Category",
            ["Technical", "Behavioral", "Situational", "Domain-specific"],
            key=f"category_{st.session_state['reset_id']}"
        )

    with col3:
        experience_level = st.selectbox(
            "Experience Level",
            ["Fresher", "Mid-level", "Senior"],
            key=f"experience_{st.session_state['reset_id']}"
        )

    # Generate Q&A with rate limiting
    can_call, wait_time = can_make_api_call()
    generate_disabled = not can_call

    if generate_disabled:
        st.warning(f"⏳ Please wait {wait_time:.1f} more seconds before making another request.")

    if st.button("Generate Interview Q&A", disabled=generate_disabled):
        if not job_or_jd.strip() and "summary_text" not in st.session_state:
            st.warning("Please enter a job role/JD or upload a PDF.")
        else:
            st.session_state["last_api_call"] = time.time()
            
            with st.spinner("Generating questions..."):
                qas = generate_qas(
                    job_or_jd,
                    st.session_state.get("summary_text", ""),
                    category,
                    difficulty,
                    experience_level
                )
                
                if qas:
                    st.session_state["qas"] = qas
                    
                    history_entry = {
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "job_or_jd": job_or_jd,
                        "document_summary": st.session_state.get("summary_text", ""),
                        "category": category,
                        "difficulty": difficulty,
                        "experience_level": experience_level,
                        "qas": qas,
                        "evaluations": []
                    }
                    st.session_state["conversation_history"].append(history_entry)
                    st.session_state["current_session_idx"] = len(st.session_state["conversation_history"]) - 1
                    st.rerun()

    if "qas" in st.session_state:
        st.markdown("### 🧠 Interview Questions & Answers")
        st.markdown(st.session_state["qas"])

    # Answer Evaluation
    if "qas" in st.session_state:
        st.markdown("### ✍️ Answer Evaluation")

        question = st.text_input(
            "Paste the question",
            key=f"eval_q_{st.session_state['reset_id']}"
        )
        user_answer = st.text_area(
            "Type your answer",
            height=150,
            key=f"user_ans_{st.session_state['reset_id']}"
        )

        can_eval, eval_wait_time = can_make_api_call()
        eval_disabled = not can_eval

        if eval_disabled:
            st.warning(f"⏳ Please wait {eval_wait_time:.1f} more seconds before evaluating.")

        if st.button("Evaluate Answer", disabled=eval_disabled):
            if not question.strip() or not user_answer.strip():
                st.warning("Please provide both question and answer.")
            else:
                st.session_state["last_api_call"] = time.time()
                
                with st.spinner("Evaluating..."):
                    feedback = evaluate_answer(question, user_answer)
                    
                    if feedback:
                        st.session_state["evaluation"] = feedback
                        
                        if "current_session_idx" in st.session_state:
                            evaluation_entry = {
                                "question": question,
                                "user_answer": user_answer,
                                "feedback": feedback
                            }
                            st.session_state["conversation_history"][st.session_state["current_session_idx"]]["evaluations"].append(evaluation_entry)
                        st.rerun()

    if "evaluation" in st.session_state:
        st.markdown("### 📊 Evaluation Result")
        st.markdown(st.session_state["evaluation"])

    # Clear Form
    st.divider()
    st.button("🧹 Clear Form", on_click=clear_and_reset)

    st.markdown('</div>', unsafe_allow_html=True)