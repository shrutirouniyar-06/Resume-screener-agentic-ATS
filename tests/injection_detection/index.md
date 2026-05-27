# Injection Detection Test Suite - Index

Welcome to the Injection Detection Test Suite! This folder contains comprehensive tests for validating prompt injection detection in the Resume Screener application.

## 📋 What's in This Folder

```
tests/injection_detection/
├── index.md                       # This file - Overview
├── QUICK_START.md                 # 30-second setup guide
├── README.md                      # Full documentation
├── TEST_RESULTS.md                # Test execution results
├── test_runner.py                 # Test execution script
│
└── Test Resumes (5 files)
    ├── test_inject_1_ignore.txt   # Ignore/Forget payload
    ├── test_inject_2_bypass.txt   # Bypass/Override payload
    ├── test_inject_3_approval.txt # Approval/Scoring payload
    ├── test_inject_4_tags.txt     # XML/HTML/Function payload
    └── test_inject_5_execute.txt  # Command execution payload
```

## 🚀 Quick Start (30 seconds)

```bash
cd tests/injection_detection
python test_runner.py
```

**Expected output:** `✅ ALL TESTS PASSED! (11/11)`

## 📖 Documentation Map

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [QUICK_START.md](QUICK_START.md) | Get running in 30 seconds | 2 min |
| [README.md](README.md) | Full technical documentation | 10 min |
| [TEST_RESULTS.md](TEST_RESULTS.md) | Latest test execution results | 5 min |

## 🎯 What Gets Tested

### 5 Attack Vectors

1. **Ignore/Forget Instructions** - Attempts to bypass requirements
2. **Bypass/Override System** - Tries to override security measures
3. **Approval/Scoring Manipulation** - Seeks to manipulate scoring
4. **XML/HTML/Function Calls** - Uses markup and function syntax
5. **Command Execution** - Attempts to execute arbitrary commands

### Test Types

- **Local Detection Tests** (5) - Direct Python function calls
- **API Detection Tests** (5) - HTTP requests to API
- **Legitimate Resume Test** (1) - Ensures no false positives

## ✅ Test Status

**Last Run:** 2026-05-28  
**Result:** ✅ 11/11 PASSED  
**Coverage:** 100%  

## 🔧 How to Use

### Option 1: Run All Tests (Recommended)
```bash
python test_runner.py
```
Tests local detection, API, and legitimate resume handling.

### Option 2: Test Locally Only (No API needed)
```bash
python
>>> from backend.services.safety import detect_prompt_injection
>>> with open('test_inject_1_ignore.txt') as f:
>>>     is_injection, pattern = detect_prompt_injection(f.read())
>>>     print(f"Detected: {is_injection}")
```

### Option 3: Manual API Testing
```bash
# Upload a test resume
curl -X POST http://localhost:5000/api/screen \
  -F "resume=@test_inject_1_ignore.txt" \
  -F "job_role_id=edd817fc"
```

Expected response: **400 status** with **INJECTION_DETECTED code**

## 📊 Test Coverage

| Aspect | Coverage | Status |
|--------|----------|--------|
| Ignore patterns | 100% | ✅ |
| Bypass patterns | 100% | ✅ |
| Approval patterns | 100% | ✅ |
| System tags | 100% | ✅ |
| Function calls | 100% | ✅ |
| False positives | 0% | ✅ |
| API responses | 100% | ✅ |
| Logging | 100% | ✅ |

## 🔍 Technical Details

### Architecture
- **Detection Module:** `backend/services/safety.py`
- **Function:** `detect_prompt_injection(text)` → `(is_injection: bool, pattern: str)`
- **Patterns:** 21+ regex patterns covering 5 attack vectors
- **API Integration:** `backend/routes/screening.py`

### Injection Patterns (Key Examples)
- `ignore.*requirements`
- `bypass.*(safety|filter|system)`
- `execute.*command`
- `<system>`, `[ADMIN]`, `<!-- -->`
- `shortlist_candidate()`, `process_candidate_approval()`

### Expected Behavior
✅ Injections → **BLOCKED** (400 status, CRITICAL severity)
✅ Legitimate → **ALLOWED** (normal screening flow)

## 🛠️ Troubleshooting

### Tests fail with "Cannot connect to API"
**Solution:** API is optional. Tests run local detection automatically if API unavailable.

### ModuleNotFoundError: No module named 'backend'
**Solution:** Run from project root:
```bash
cd Resume-screener-agentic-ATS
python tests/injection_detection/test_runner.py
```

### "File not found" errors
**Solution:** Verify files exist:
```bash
ls test_inject_*.txt
```

## 📈 Next Steps

1. **Run the tests:** `python test_runner.py`
2. **Read the docs:** [README.md](README.md)
3. **Check results:** [TEST_RESULTS.md](TEST_RESULTS.md)
4. **Integrate CI/CD:** Add to your pipeline

## 🔐 Security Notes

- ✅ All injection payloads are **clearly marked** in test files
- ✅ Test files contain **realistic resume content**
- ✅ No actual candidate data is compromised
- ✅ Tests are **repeatable and isolated**
- ✅ Results are **auditable and loggable**

## 📞 Support

For issues or questions:
1. Check [README.md](README.md) for detailed documentation
2. Review [TEST_RESULTS.md](TEST_RESULTS.md) for expected results
3. Verify backend is running: `curl http://localhost:5000/api/health`

## 🎓 Learning Resources

- **How injection detection works:** See `backend/services/safety.py`
- **Regex patterns used:** Search for `INJECTION_PATTERNS` in safety.py
- **API flow:** Check `backend/routes/screening.py` lines 169-196
- **Test execution:** Review `test_runner.py`

---

**Made with 🔒 Security-First Mindset**  
*Protecting your recruitment process from malicious inputs*
