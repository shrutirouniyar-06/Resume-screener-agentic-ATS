# ✅ Quick Checklist - Before You Start

## Pre-Setup (5 min)
- [ ] Ensure Python 3.8+ installed: `python --version`
- [ ] Ensure Node.js 16+ installed: `node --version`
- [ ] Get API key from one provider:
  - [ ] GROQ: https://console.groq.com/keys
  - [ ] HuggingFace: https://huggingface.co/settings/tokens
  - [ ] OpenRouter: https://openrouter.ai/keys

## Configuration (2 min)
- [ ] Open `backend/.env`
- [ ] Set `PROVIDER=GROQ` (or HUGGINGFACE / OPENROUTER)
- [ ] Add your API key
- [ ] Save the file

## Start Backend (1 min)
```bash
cd backend
python app.py
```
- [ ] See message: "Using GROQ provider"
- [ ] See message: "Running on http://127.0.0.1:5000"
- [ ] Test: `curl http://localhost:5000/api/health`

## Start Frontend (1 min - new terminal)
```bash
cd frontend
npm run dev
```
- [ ] See message: "Local: http://localhost:5173"

## First Run (2 min)
- [ ] Open http://localhost:5173 in browser
- [ ] See logo and navigation
- [ ] Click "Job roles" tab
- [ ] Click "New role" button
- [ ] Create a test role (e.g., "Senior Engineer")
- [ ] Click "AI Generate" (or manually configure)

## Test Upload (2 min)
- [ ] Go to "Upload resumes" tab
- [ ] Drag a test resume PDF
- [ ] See file size displayed ✅
- [ ] Select your job role
- [ ] Click "Screen resumes"
- [ ] Watch progress bar ✅
- [ ] See completion message ✅

## Done! 🎉
- [ ] All tests passed
- [ ] Ready to screen real resumes
- [ ] Phase 1 working perfectly

---

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Backend won't start | Check .env file exists and API key is set |
| Frontend won't load | Check backend is running on port 5000 |
| API key errors | Verify key format matches provider (gsk_ for GROQ, hf_ for HF) |
| No roles showing | Create a role first in "Job roles" tab |
| File upload fails | Check file is under 10MB |

---

## Important Files to Know

**Config:** `backend/.env`  
**Quick Start:** `GETTING_STARTED.md`  
**Setup Help:** `SETUP_GUIDE.md`  
**Startup:** `START_SERVERS.bat` (Windows) or `START_SERVERS.sh` (Mac/Linux)  

---

Time to completion: **~15 minutes** ⏱️
