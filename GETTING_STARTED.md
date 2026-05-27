# 🚀 Getting Started - Screen-U Resume Screener

## ⚡ 30-Second Quick Start

### Step 1: Add API Keys
Edit `backend/.env` and add ONE of these:

```env
# GROQ (Fastest, Recommended)
PROVIDER=GROQ
GROQ_API_KEY=your_key_here
GROQ_MODEL=mixtral-8x7b-32768
```

### Step 2: Run
```bash
# Windows: Double-click this
START_SERVERS.bat

# Mac/Linux: Run this
./START_SERVERS.sh
```

### Step 3: Open Browser
```
http://localhost:5173
```

**Done!** Start creating job roles and screening resumes. ✅

---

## 📋 Detailed Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- An API key from one of: GROQ, HuggingFace, or OpenRouter

### 1. Configure Your LLM Provider

**File:** `backend/.env`

Choose **ONE** provider and add credentials:

#### 🟦 GROQ (Fastest, Free tier available)
```env
PROVIDER=GROQ
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxx
GROQ_MODEL=mixtral-8x7b-32768
```
📍 Get key: https://console.groq.com/keys

#### 🟨 HuggingFace
```env
PROVIDER=HUGGINGFACE
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxx
HF_MODEL=meta-llama/Llama-2-7b-chat-hf
```
📍 Get key: https://huggingface.co/settings/tokens

#### 🔴 OpenRouter
```env
PROVIDER=OPENROUTER
OPENROUTER_API_KEY=sk_xxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=meta-llama/llama-2-70b-chat
```
📍 Get key: https://openrouter.ai/keys

---

### 2. Start the Backend

```bash
cd backend
python app.py
```

✅ Expected output:
```
Using GROQ provider, Model: mixtral-8x7b-32768
 * Running on http://127.0.0.1:5000
```

**Test it:**
```bash
curl http://localhost:5000/api/health
# {"status": "ok", "model": "mixtral-8x7b-32768"}
```

---

### 3. Start the Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

✅ Expected output:
```
  ➜  Local:   http://localhost:5173/
```

---

## 🎯 Using Screen-U

### Create a Job Role

1. Click **"Job roles"** in sidebar
2. Click **"New role"** button
3. Enter:
   - **Role title:** e.g., "Senior Backend Engineer"
   - **Department:** e.g., "Engineering"
   - **Description:** e.g., "5+ years experience with Python and AWS"

4. **Option A:** Click **"AI Generate"** (auto-populates skills from title)
   - OR **Option B:** Click **"Create role"** (manual configuration later)

5. Configure scoring rules:
   - Skill weights (importance of each skill)
   - Experience bands (score multipliers)
   - Threshold (% score to shortlist)

### Screen Resumes

1. Click **"Upload resumes"** in sidebar
2. Drag-and-drop files or click to browse
   - Supported: PDF, DOCX, TXT
   - Max size: 10MB per file
3. Select a **job role** from dropdown
4. Click **"Screen resumes"**
5. Watch the progress bar! ✅

### View Results

1. Click **"Dashboard"** to see pipeline overview
2. Click on any candidate to see:
   - Match score breakdown (skills, experience, profile quality)
   - Status (Shortlisted / Rejected)
   - If Shortlisted: Generated interview questions
   - If Rejected: Feedback and improvement suggestions
   - AI recruiter summary

### Rate Interview Responses (Optional)

1. Go to candidate detail
2. Click **"Interview Profile"**
3. Rate each question by competency (1-5 scale)
4. Ratings saved automatically

---

## ✨ Phase 1 Improvements (Just Shipped!)

### ✅ File Validation
- Files showing size in KB/MB format
- 10MB size limit enforced
- Warning if file exceeds limit

### ✅ Loading Progress
- Progress bar during screening
- "X of Y completed" counter
- File status icons (pending → processing → done)

### ✅ Success/Error Messages
- Green success message when all done
- Red error message with count if failures
- "2 successful • 1 failed" summary

### ✅ Form Validation
- Role title required (3-100 chars)
- Department validated (max 50 chars)
- Description validated (max 500 chars)
- Clear error messages below form

---

## 🔧 Troubleshooting

### Backend won't start

**Error: "Missing environment variables"**
- [ ] Check `backend/.env` exists
- [ ] Check you set PROVIDER to one of: GROQ, HUGGINGFACE, OPENROUTER
- [ ] Check API key is filled in (not empty)

**Error: "Connection refused" or "Port already in use"**
```bash
# Kill existing process on port 5000
lsof -ti:5000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5000   # Windows (then kill PID)
```

**Error: "ModuleNotFoundError"**
```bash
cd backend
pip install -r requirements.txt
```

---

### Frontend won't load

**Error: "Cannot find module"**
```bash
cd frontend
npm install
```

**Error: "Backend not responding"**
- [ ] Is backend running on http://localhost:5000?
- [ ] Try: `curl http://localhost:5000/api/health`
- [ ] If nothing, backend crashed. Check Flask logs.

**Page shows "No roles yet"**
- [ ] Go to "Job roles" tab
- [ ] Click "New role"
- [ ] Create one manually

---

### LLM API fails during screening

**Error: "LLM analysis failed"**
- [ ] Verify API key is correct in `.env`
- [ ] Check your API quota/balance
- [ ] Verify internet connection
- [ ] Try a different provider
- [ ] Check API provider status page

---

## 📊 Project Architecture

```
┌─────────────────────────────────────────┐
│          React Frontend (Port 5173)      │
│  ├─ Dashboard (candidate pipeline)       │
│  ├─ Job Roles (CRUD + scoring config)    │
│  ├─ Upload Page (resume screening)       │
│  └─ Interview Page (question rating)     │
└────────────────┬────────────────────────┘
                 │ (HTTP/JSON)
┌────────────────▼────────────────────────┐
│       Flask Backend (Port 5000)          │
│  ├─ /api/roles (job role management)     │
│  ├─ /api/screen (resume screening)       │
│  ├─ /api/candidates (results storage)    │
│  └─ /api/stats (pipeline metrics)        │
└────────────────┬────────────────────────┘
                 │ (REST API)
         ┌───────┴──────────┐
         │                  │
    ┌────▼──────┐    ┌─────▼────┐
    │  LLM API  │    │  In-Memory│
    │ (GROQ/HF) │    │   Store   │
    └───────────┘    └───────────┘
```

**Note:** In-memory storage will be replaced with SQLite/PostgreSQL in Phase 2.

---

## 📚 What's Next?

### Phase 2 (Coming Soon)
- 🗄️ **Persistent Database** - Replace in-memory with SQLite
- 📊 **Analytics Dashboard** - Candidate metrics and pipeline visualization
- 📈 **Reports Page** - Export data, view trends

### Phase 3
- 📝 **Enhanced Documentation** - Architecture diagrams
- 🔍 **Logging & Observability** - Track API calls and operations
- ⚡ **Performance Optimization** - Batch processing, caching

---

## 📞 Support

- **Setup issues?** Check `SETUP_GUIDE.md`
- **Phase 1 complete?** See `PHASE_1_COMPLETE.md`
- **Environment help?** Check `.env` template in `backend/.env`

---

## ✅ Checklist Before You Start

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] API key obtained (GROQ / HuggingFace / OpenRouter)
- [ ] `backend/.env` configured with your key
- [ ] Backend runs without errors
- [ ] Frontend loads in browser
- [ ] Demo role appears on Dashboard

**All checked?** You're ready to screen resumes! 🎉

---

**Happy Screening!** 🚀
