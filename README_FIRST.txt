╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║           🚀 SCREEN-U RESUME SCREENER - QUICK START            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

STEP 1: Add Your LLM API Keys
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Edit: backend/.env
  
  Choose ONE provider and add your API key:
  
  GROQ (Recommended - Free tier):
    PROVIDER=GROQ
    GROQ_API_KEY=your_key_here
    GROQ_MODEL=mixtral-8x7b-32768
  
  Or HuggingFace:
    PROVIDER=HUGGINGFACE
    HF_TOKEN=your_token_here
    HF_MODEL=meta-llama/Llama-2-7b-chat-hf
  
  Or OpenRouter:
    PROVIDER=OPENROUTER
    OPENROUTER_API_KEY=your_key_here
    OPENROUTER_MODEL=meta-llama/llama-2-70b-chat


STEP 2: Start the Servers
━━━━━━━━━━━━━━━━━━━━━━━━━
  
  Windows:
    Double-click: START_SERVERS.bat
  
  Mac/Linux:
    Run: ./START_SERVERS.sh


STEP 3: Open Browser
━━━━━━━━━━━━━━━━━━━
  
  Go to: http://localhost:5173


That's it! Start screening resumes! 🎉


📚 Documentation Files
━━━━━━━━━━━━━━━━━━━━━━
  • GETTING_STARTED.md ........... Complete setup guide
  • SETUP_GUIDE.md ............... LLM provider options
  • PHASE_1_COMPLETE.md .......... What was implemented
  • README.md .................... Project overview


✨ What Was Just Added (Phase 1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ File size display (shows KB/MB on upload)
  ✅ File validation (10MB max, clear warnings)
  ✅ Loading progress bar (with % completion)
  ✅ Success/error messages (with counts)
  ✅ Form validation (job role creation)
  ✅ Better error messages (inline feedback)


🔧 Troubleshooting
━━━━━━━━━━━━━━━━━━
  See GETTING_STARTED.md → "Troubleshooting" section


🎯 Next Steps
━━━━━━━━━━━━
  Phase 2: Database persistence & analytics dashboard
  Phase 3: Enhanced documentation & logging


Questions? → Check GETTING_STARTED.md

Happy screening! 🚀
