# Screen-U - Recruitment Intelligence (Updated v2.2)

Screen-U is a web application designed to automate and supercharge the initial resume screening process. It operates as a clean, utilitarian SaaS platform for recruiters, enabling them to make faster, data-driven decisions.

The system takes a candidate's resume, compares it against a highly configurable Job Role, calculates a detailed match score, and then generates tailored content like interview questions for promising candidates or constructive feedback for those who don't meet the threshold.

**Enhanced in v2.2 with persistent database architecture, comprehensive AI safety mechanisms, and role-based skill matching to improve hiring transparency and security.**

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+ with npm
- HuggingFace API credentials

### Backend Setup

1. Navigate to backend directory:
   ```sh
   cd backend
   ```

2. Create and activate virtual environment:
   ```sh
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```sh
   export HF_TOKEN=your_huggingface_token
   ```

5. Start development server:
   ```sh
   python app.py
   ```
   Backend available at `http://127.0.0.1:5000`

### Frontend Setup

1. Navigate to frontend directory:
   ```sh
   cd frontend
   ```

2. Install dependencies:
   ```sh
   npm install
   ```

3. Start development server:
   ```sh
   npm run dev
   ```
   Frontend available at `http://localhost:5173`

## Features

### Brownfield Improvements in v2.2

**Code Quality Issue #1 - In-Memory Data Loss**
- Problem: All candidate data and screening results were lost on server restart, making the application unsuitable for production
- Solution: Implemented SQLite persistent database layer with transactional consistency ensuring data continuity across server restarts and session refreshes

**Code Quality Issue #2 - State Type Inconsistency**
- Problem: Malware detection flag rendered as integer (0) in UI instead of boolean, breaking conditional rendering logic
- Solution: Enhanced state management with proper type conversion ensuring malware_detected is boolean throughout the stack (backend API, frontend state, conditional rendering)

### Core Features

- **Job Role Management**: Create, read, update, and delete job roles with role-specific scoring configurations.
- **Configurable Scoring Engine**:
    - Skill Weighting: Adjust relative importance of required competencies.
    - Experience Bands: Define multiplier functions based on years of experience.
    - Penalty Rules: Apply deductions for employment gaps and job-hopping patterns.
    - Bias Safeguards: Implement name, university, and graduation year anonymization.
- **Persistent Candidate Storage**: SQLite database maintaining screening results and historical data across sessions.
- **AI Safety Infrastructure**:
    - Prompt injection attack detection and classification
    - Malware feedback generation with attack details
    - Bias and fairness assessment in screening decisions
    - Hallucination detection and validation
    - LLM output structural validation
- **Automated Content Generation**:
    - Interview question generation for shortlisted candidates.
    - Rejection feedback with constructive improvement suggestions.
    - Candidate summary generation highlighting strengths and competency gaps.
- **Voice Interview for Soft Skills Assessment**:
    - Automated speech-to-text processing with communication quality metrics.
    - Soft skills evaluation: clarity score, confidence assessment, response relevance, speaking pace analysis.
    - Communication scoring integrated with overall candidate profile.
    - Holistic evaluation combining technical skills with interpersonal competencies.
- **Demo Mode**: Pre-configured job roles enabling immediate evaluation.

### UI/UX Enhancements in v2.2

**Dark Mode Text Visibility**
- Problem: When toggling dark mode theme, text elements were not rendering with proper contrast and visibility
- Solution: Fixed dark mode color contrast and typography rendering with enhanced styling ensuring text legibility in both light and dark themes

**Skill Matching Display**
- Implementation: Role-based deterministic skill mapping for 12 job classifications
- Prevents hallucinations about candidate qualifications not present in resume
- Returns hyphen indicator ("—") when no skills are matched, improving clarity for candidates with skill gaps

**Dashboard Grid Refinement**
- Enhanced grid layout with consistent badge alignment and spacing
- Resume upload timestamp tracking for chronological organization
- Malware detection indicators with contextual hover information
- Improved visual hierarchy and typography across candidate listings

## Architecture

### Tech Stack

- **Frontend**: React with enhanced styling and theme management
- **Backend**: Flask (Python) with modular service architecture
- **Database**: SQLite with transactional consistency
- **AI/ML**: HuggingFace Inference API for NLP tasks
- **Safety**: Regex-based pattern matching, statistical bias detection
- **Resume Parsing**: Text format support (PDF and DOCX formats planned for future release)
- **Voice Interview**: Speech-to-text processing and soft skills assessment

### Screening Pipeline with Safety Layer

1. File ingestion with type validation
2. Prompt injection pattern detection
3. Resume content extraction
4. LLM analysis and scoring
5. Hallucination detection and validation
6. Bias assessment in evaluation
7. Malware feedback generation
8. Persistent database storage with metadata

### Core Services

- `safety.py`: Multi-mechanism safety implementation (injection, bias, hallucination detection)
- `scraper.py`: Role-based skill mapping to match candidate skills with specific job requirements
- `parser.py`: Resume text extraction and normalization
- `store_sqlite.py`: Persistence layer and schema management

## AI Capabilities Used

### Prompt Injection Detection

Detects and classifies malicious resume instructions:
- 21+ patterns covering known attack methodologies
- Attack vector classification (ignore, bypass, manipulation, injection, execution)
- Detailed malware feedback with attack method and security impact
- Prevents unauthorized candidate approvals

### LLM Output Validation

- Numeric range enforcement (0-100 score bounds)
- Structural field validation
- Prevents malformed or hallucinated data from influencing decisions

### Fairness & Bias Detection

- Protected characteristic detection in evaluation language
- Discriminatory pattern identification
- EEOC and employment law compliance enforcement
- Prevents demographic-based decision factors

### Hallucination Validation

- Keyword overlap analysis between resume and LLM output
- Validates that skill suggestions are missing from resume content
- Prevents false qualification attribution
- Improves assessment accuracy

### Role-Based Skill Mapping

Deterministic skill mapping based on job role preventing generic LLM suggestions:
- Maps candidate skills to specific job role requirements
- Returns relevant skill matches for each role type
- Prevents hallucinated skills unrelated to the position

### Voice Interview Analysis

- Speech-to-text conversion for asynchronous candidate assessment
- Communication quality metrics extraction
- Soft skills scoring based on clarity, confidence, relevance, speaking pace

## API Endpoints

- `GET, POST /api/roles`: Role management operations
- `GET, PUT, DELETE /api/roles/<id>`: Role-specific operations and configuration
- `POST /api/screen`: Resume screening with multipart form data (resume file, job_role_id)
- `GET /api/candidates`: Retrieve candidate list with analysis metadata
- `GET /api/candidates/<id>`: Detailed candidate profile including malware feedback

## Testing & Validation

### Prompt Injection Detection Suite

Execute comprehensive safety validation:

```bash
python tests/injection_detection/test_runner.py
```

Test results: 5/5 local injection detection tests passing

Coverage:
- Ignore/Forget instruction attacks
- Bypass/Override system attacks
- Scoring manipulation attacks
- XML tag injection attacks
- Command execution attacks

## Challenges Faced

**Challenge #1: Data Persistence & State Management**
- In-memory storage caused complete data loss on restart, making the application unsuitable for production use
- Solution: Migrated to SQLite with proper schema design and transactional consistency

**Challenge #2: LLM Hallucination in Skill Suggestions**
- Generic LLM-based skill recommendations were inaccurate and role-irrelevant, causing false candidate qualifications
- Solution: Implemented deterministic role-based skill mapping for 12 job types, eliminating hallucinations

**Challenge #3: AI Safety in Recruiting**
- Resume screening systems are vulnerable to prompt injection attacks designed to manipulate hiring decisions
- Solution: Built comprehensive safety layer with 21+ injection patterns, malware feedback, bias detection, and hallucination validation

**Challenge #4: UI/UX Theme Rendering**
- Dark mode toggle was breaking text visibility and component styling
- Solution: Enhanced color contrast and typography with proper theme-aware styling

**Challenge #5: Data Type Consistency**
- Boolean flags rendered as integers in frontend, breaking conditional logic
- Solution: Implemented proper type conversion throughout the stack (backend API, state management, rendering)

## Documentation

Comprehensive implementation documentation organized by development phases is available in the `/docs` folder:

- **Phase 1**: Foundation and brownfield improvements
- **Phase 2**: AI safety mechanisms and database persistence
- **Phase 2.1**: SQLite implementation and malware detection
- **Phase 2.2**: Voice interview integration and role-based skill matching

Documentation includes setup guides, AI safety implementation details, quick start references, and implementation checklists.

## Future Roadmap

- **Batch Processing**: Parallel resume screening with job queue management
- **Analytics Dashboard**: Hiring funnel metrics, time-to-hire notifications, and candidate flow analysis
- **Extended Parsing**: PDF and DOCX format support for resume processing
- **Compliance Reporting**: Automated regulatory compliance documentation (EEOC, GDPR)
- **Multilingual Support**: Resume screening across multiple language contexts
- **Custom Evaluation Framework**: Recruiter-defined scoring rule configuration
- **External Integration**: Third-party ATS platform connectors and job board APIs

---

*Screen-U v2.2 - Production-ready with AI safety, persistent storage, and intelligent skill matching*
