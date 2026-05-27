# 🚀 Quick Start Guide - Screen-U

## Step 1: Configure Your LLM Provider

Edit `backend/.env` and add your API credentials. Choose **ONE** provider:

### Option A: GROQ (Recommended - Fastest & Free)
```bash
PROVIDER=GROQ
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768  # or llama2-70b-4096
```
**Get API Key:** https://console.groq.com/keys

### Option B: HuggingFace
```bash
PROVIDER=HUGGINGFACE
HF_TOKEN=your_hf_token_here
HF_MODEL=meta-llama/Llama-2-7b-chat-hf
```
**Get API Key:** https://huggingface.co/settings/tokens

### Option C: OpenRouter
```bash
PROVIDER=OPENROUTER
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=meta-llama/llama-2-70b-chat
```
**Get API Key:** https://openrouter.ai/keys

---

## Step 2: Start the Backend

```bash
cd backend
python app.py
```

✅ You should see:
```
Using GROQ provider, Model: mixtral-8x7b-32768
 * Running on http://127.0.0.1:5000
```

Test it:
```bash
curl http://localhost:5000/api/health
```

---

## Step 3: Start the Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

✅ You should see:
```
  ➜  Local:   http://localhost:5173/
```

Open http://localhost:5173 in your browser!

---

## 📋 What You Can Do Now

### 1. **Create Job Roles**
   - Navigate to **"Job roles"** tab
   - Click **"New role"** 
   - Enter role title, department, description
   - Use **"AI Generate"** to auto-populate skills from job title (or configure manually)

### 2. **Upload & Screen Resumes**
   - Go to **"Upload resumes"**
   - Drag-and-drop PDF/DOCX/TXT files (max 10MB each)
   - Select a job role
   - Click **"Screen resumes"** and watch the progress!

### 3. **View Results**
   - Dashboard shows candidate pipeline
   - Click on each candidate to see:
     - Match score breakdown
     - Shortlist status
     - Auto-generated interview questions OR rejection feedback
     - AI recruiter summary

### 4. **Rate Interview Responses** (optional)
   - Go to candidate detail
   - Click "Interview Profile"
   - Rate competencies for each question

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if Python 3.8+ is installed
python --version

# Install dependencies
pip install -r requirements.txt

# Check .env file is in backend/ folder
ls backend/.env
```

### Frontend won't load
```bash
# Make sure backend is running on port 5000
curl http://localhost:5000/api/health

# Install frontend dependencies
npm install

# Start dev server
npm run dev
```

### LLM API fails
- Verify API key is correct in `.env`
- Check token/key has appropriate permissions
- Try a different provider
- Check your API quota/balance

---

## 📝 Environment Variables Summary

| Variable | Required | Example |
|----------|----------|---------|
| `PROVIDER` | ✅ Yes | `GROQ` \| `HUGGINGFACE` \| `OPENROUTER` |
| `GROQ_API_KEY` | If GROQ | `gsk_...` |
| `GROQ_MODEL` | If GROQ | `mixtral-8x7b-32768` |
| `HF_TOKEN` | If HF | `hf_...` |
| `HF_MODEL` | If HF | `meta-llama/Llama-2-7b-chat-hf` |
| `OPENROUTER_API_KEY` | If OpenRouter | `sk-...` |
| `OPENROUTER_MODEL` | If OpenRouter | `meta-llama/llama-2-70b-chat` |

---

## 🎯 Next Steps

After confirming everything works:

1. **Phase 2:** Add persistent database (SQLite → PostgreSQL)
2. **Phase 2:** Build analytics dashboard with real data
3. **Phase 3:** Add logging & observability
4. **Phase 3:** Update README with architecture docs

Happy screening! 🎉
