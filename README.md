# Interview Q&A Generator

> AI-powered interview preparation tool with context-aware question generation, answer evaluation, and progress tracking.

---

## Table of Contents

- Overview
- Features
- Installation
- Usage
- Project Structure
- Configuration
- TRoubkeshooting
- Contributing
- License

---

## Overview

The Interview Q&A Generator is a comprehensive interview preparation platform that leverages Google's Gemini 2.5 Flash AI model to help job seekers practice and improve their interview skills. Upload your resume or job description, customize question types, practice answering, and receive AI-powered feedback with actionable improvement suggestions.

**Built with:** Streamlit • Google Gemini AI • PyMuPDF • FPDF

---

## Features

### 🤖 AI-Powered Question Generation
- Generate 4 customized interview questions with detailed model answers
- Questions adapt to job role, resume content, and your preferences
- Intelligent caching reduces API usage and improves speed

### 📄 Document Analysis & Context
- Upload PDF resumes or job descriptions (up to 5 pages)
- Automatic AI-powered document summarization
- Extracts key information: skills, experience, requirements
- Questions tailored to match your background with job needs

### 📝 Answer Evaluation System
- Submit your answers for AI-powered feedback
- Scored on three criteria:
  - Completeness (0-3 points)
  - Technical Accuracy (0-4 points)
  - Communication Clarity (0-3 points)
- Receive detailed feedback with strengths and improvement areas
- Get suggested enhanced answers

### 🎯 Customization Options
- **Difficulty Levels:** Easy, Medium, Hard
- **Categories:** Technical, Behavioral, Situational, Domain-specific
- **Experience Levels:** Fresher (0-2 yrs), Mid-level (2-5 yrs), Senior (5+ yrs)

### 📊 Session Management
- Automatic tracking of all Q&A sessions
- View complete history in sidebar
- Load and review previous sessions
- Track all answer evaluations

### 📤 Export Functionality
- **PDF Export:** Professional formatted document
- **Text Export:** Plain text for easy sharing
- **JSON Export:** Structured data for analysis

### 🚀 Smart Performance Features
- Intelligent caching system (reduces redundant API calls)
- Rate limiting protection (5-second minimum between calls)
- Exponential backoff retry logic for failed requests
- Comprehensive error handling with user-friendly messages
- Progress indicators and visual feedback

---


### Sample Output

**Generated Questions:**
```
Q1. What is machine learning?
A1.Training machine to give solutions like humans.
```

**Answer Evaluation:**
```
   **Rating:** Very Low
*   **Feedback:** The answer is extremely brief and only touches upon a single, high-level aspect of machine learning. It
misses crucial components of a comprehensive definition, such as:
    *   The role of **data** as the source of learning.
    *   The process of identifying **patterns** or **rules**.
    *   The use of **algorithms**.
    *   The goal of **generalization** to new, unseen data.
    *   The idea of learning **from experience** or examples without explicit programming for every specific outcome.
### 2. Technical Accuracy
*   **Rating:** Moderate
*   **Feedback:**
    *   "Training machine to give solutions" is fundamentally accurate in spirit; machine learning *does* involve training
systems to solve problems.
    *   However, "like humans" is an oversimplification and can be misleading. While Artificial Intelligence (of which ML is
a subfield) often seeks to mimic human intelligence, not all machine learning explicitly aims to behave "like humans."
Many ML applications focus on statistical pattern recognition, prediction, or optimization tasks that don't have a direct
human analogy or aim. It also conflates ML with the broader goal of Artificial General Intelligence.
### 3. Communication Clarity
*   **Rating:** High
*   **Feedback:** The answer is very clear, concise, and easy to understand. It uses simple language, which is a strong
point.--
### Score: 3/10
### Feedback:
The answer is commendable for its clarity and conciseness. You've captured a very high-level intuition that machine
learning involves training systems to solve problems. However, it severely lacks the depth and key technical details
expected in a definition of machine learning. The "like humans" part, while inspirational for AI in general, is an
oversimplification for the vast field of machine learning and can be technically imprecise. For an interview, this answer
would indicate a very basic, superficial understanding.
### Improvements:
1.  **Incorporate "Data":** Emphasize that machines learn *from data*.
2.  **Mention "Patterns" or "Rules":** Explain that the learning process involves identifying patterns or rules within that
data.
3.  **Specify the Goal:** Clarify that the goal is often to make predictions, classifications, or decisions on *new, unseen
data*.
4.  **Differentiate from Traditional Programming:** Briefly explain that it's about learning from examples rather than
explicit, hand-coded rules for every scenario.
5.  **Refine "Like Humans":** Consider if this analogy is truly necessary for a core definition of ML. If you use it, qualify it
carefully (e.g., "to perform tasks that traditionally require human intelligence").
**Example of an improved answer:**
"Machine learning is a field of artificial intelligence that enables systems to *learn from data* to identify patterns and
make predictions or decisions, *without being explicitly programmed* for every specific task. Instead of following rigid
instructions, these systems use algorithms to learn from examples and improve their performance over time."s
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one free here](https://aistudio.google.com/app/apikey))
- pip package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/SANIKAPETK/Interview-Q-A-Generator.git
cd Interview-Q-A-Generator
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up API Key

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. Create the `.streamlit` directory and `secrets.toml` file:

**Windows:**
```bash
mkdir .streamlit
notepad .streamlit\secrets.toml
```

**macOS/Linux:**
```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

3. Add your API key to the file:

```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

4. Save and close the file

### Step 5: Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## Usage

### 1. Generate Interview Questions

**Option A: Using Job Role**
1. Type a job title (e.g., "Software Engineer") in the text area
2. OR paste a complete job description

**Option B: Upload Document**
1. Click "Upload PDF" button
2. Select your resume or job description PDF
3. Wait for AI to analyze and generate summary (5-10 seconds)
4. Review the extracted information

**Customize Your Questions**
1. Select **Difficulty**: Easy, Medium, or Hard
2. Choose **Category**: Technical, Behavioral, Situational, or Domain-specific
3. Pick **Experience Level**: Fresher, Mid-level, or Senior

**Generate**
1. Click "Generate Interview Q&A" button
2. Wait 5-10 seconds for AI processing
3. Review 4 questions with detailed answers

### 2. Evaluate Your Answers

1. Copy any generated question
2. Paste it in the "Paste the question" field
3. Type your answer in the answer text area
4. Click "Evaluate Answer" button
5. Review your score and feedback:
   - Overall score out of 10
   - Breakdown by criteria
   - Specific strengths
   - Areas for improvement
   - Suggested enhanced answer

### 3. Manage Sessions

**View History**
- Open the sidebar to see all previous sessions
- View total sessions and evaluations count

**Load Previous Session**
1. In sidebar, expand any session
2. Click "Load Session" button
3. Review all questions and evaluations from that session
4. Click "Close Loaded Session" to return

**Export Your Data**
- Click **📄 TXT** for plain text export
- Click **📕 PDF** for formatted document
- Click **💾 JSON** for structured data

**Clear History**
- Click "🗑️ Clear History" in sidebar
- Removes all saved sessions (cannot be undone)

### 4. Clear Form

- Click "🧹 Clear Form" to reset all input fields
- Session history is preserved

---

## Project Structure

```
Interview-Q-A-Generator/
│
├── app.py                      # Main application (700+ lines)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── IMPLEMENTATION.md           # Implementation details
├── LICENSE                     # MIT License
│
├── .streamlit/
│   ├── secrets.toml           # API keys (NOT in git)
│   └── config.toml            # Streamlit settings
│
└── .gitignore                 # Files to exclude from git
```

---

## Configuration

### API Rate Limits

**Gemini Free Tier:**
- 15 requests per minute
- 1,500 requests per day

**App Rate Limiting:**
- Minimum 5-second delay between API calls
- Visual countdown timer shown when limit active
- Automatic retry with exponential backoff on failures

### Caching System

The app caches:
- **Document summaries** (by file hash)
- **Question sets** (by parameters)
- **Benefits:** Faster responses, reduced API usage, quota savings

### PDF Processing Limits

- Maximum pages processed: 5 pages
- Maximum characters: 6,000 per document
- Automatic truncation with notification

---

## Troubleshooting

### Common Issues and Solutions

**Issue:** API Rate Limit Exceeded (429 Error)

```
Error: 429 Rate Limit
```

**Solutions:**
- Wait 60 seconds before making another request
- Check your API quota at https://aistudio.google.com/app/apikey
- App automatically retries with delays: 5s, 10s, 20s, 40s
- Use cached results when uploading same documents

---

**Issue:** Server Overloaded (503 Error)

```
Error: 503 Service Unavailable
```

**Solutions:**
- App automatically retries with delays: 3s, 6s, 12s, 24s
- High demand on Gemini servers (usually temporary)
- Try during off-peak hours if persistent

---

**Issue:** API Key Invalid

```
Error: Failed to initialize Gemini API
```

**Solutions:**
- Verify API key in `.streamlit/secrets.toml`
- Ensure no extra spaces or quotes
- Generate a new API key if needed
- Check file is in correct location

---

**Issue:** PDF Upload Fails

```
Error: Cannot read PDF
```

**Solutions:**
- Ensure PDF is not password-protected
- Check file is not corrupted
- Verify file size is reasonable (< 10MB)
- Try re-saving PDF from a PDF reader

---

**Issue:** Questions Not Generating

**Possible Causes:**
- Empty job description field
- Rate limit cooldown active
- API quota exhausted

**Solutions:**
- Ensure job role/JD field has text
- Wait for rate limit countdown (5 seconds)
- Check API call counter in sidebar
- Try uploading PDF for better context

---

### Rate Limiting Best Practices

**DO:**
- ✅ Wait at least 5 seconds between requests
- ✅ Use caching (same inputs = cached response)
- ✅ Upload documents once, generate multiple sets
- ✅ Monitor API call counter

**DON'T:**
- ❌ Click "Generate" button multiple times rapidly
- ❌ Clear cache unnecessarily
- ❌ Open multiple tabs simultaneously

---

## Contributing

Contributions are welcome! Here's how to contribute:

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/SANIKAPETK/Interview-Q-A-Generator.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test thoroughly

4. **Commit your changes**
   ```bash
   git commit -m "Add: Your feature description"
   ```

5. **Push to your branch**
   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Open a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Wait for review

### Contribution Guidelines

- Write clear, commented code
- Follow PEP 8 style guidelines for Python
- Test all changes before submitting
- Update documentation if needed
- Be respectful in discussions

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Summary:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ Liability and warranty not provided

---

## Acknowledgments

Special thanks to:

- **[Streamlit](https://streamlit.io/)** - For the amazing web framework
- **[Google Gemini](https://ai.google.dev/)** - For the powerful AI model
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** - For PDF processing
- **[FPDF](http://www.fpdf.org/)** - For PDF generation

---

## System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- 100MB free disk space
- Internet connection
- Modern web browser

**Recommended:**
- Python 3.10+
- 4GB RAM
- SSD storage
- Stable broadband connection

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **AI Model** | Google Gemini 2.5 Flash |
| **PDF Processing** | PyMuPDF (fitz) |
| **PDF Generation** | FPDF |
| **Language** | Python 3.8+ |
| **Deployment** | Streamlit Cloud |

---

## Features Checklist

- [x] PDF document upload and processing
- [x] AI-powered document summarization
- [x] Context-aware question generation
- [x] Customizable difficulty and categories
- [x] Answer evaluation with detailed feedback
- [x] Session history tracking
- [x] Multiple export formats (PDF, TXT, JSON)
- [x] Smart caching system
- [x] Rate limiting protection
- [x] Error handling and retry logic
- [x] Modern UI with progress indicators

---

## Project Statistics

- **Total Lines of Code:** ~700+
- **Main Technologies:** 4 (Streamlit, Gemini, PyMuPDF, FPDF)
- **Supported File Types:** PDF
- **Export Formats:** 3 (PDF, TXT, JSON)
- **Question Categories:** 4
- **Difficulty Levels:** 3
- **Experience Levels:** 3

---

## Contact & Support

**Project Maintainer:** SANIKAPETK

**Repository:** https://github.com/SANIKAPETK/Interview-Q-A-Generator

**Issues & Bug Reports:** [Create an issue](https://github.com/SANIKAPETK/Interview-Q-A-Generator/issues)

**Questions?** Open a discussion or create an issue on GitHub.

---

## Roadmap

### Planned Features

- [ ] Multi-language support (Hindi, Spanish, French)
- [ ] Multi-API support
- [ ] Progress analytics dashboard
- [ ] Mock interview timer mode
  

---

---



*Last Updated: January 2026*
