# Test Suite Setup and Execution Guide

## Overview

This folder contains a complete test suite for prompt injection detection in the Resume Screener application. The test suite includes:

- **5 test resumes** with various injection payloads
- **Python test runner** with comprehensive validation
- **Complete documentation** with examples
- **Batch/Shell scripts** for easy execution

## Project Structure

```
Resume-screener-agentic-ATS/
├── backend/
│   ├── services/
│   │   └── safety.py              # Injection detection logic
│   ├── routes/
│   │   └── screening.py           # API endpoint with injection checks
│   └── main.py                    # Backend server
│
└── tests/
    └── injection_detection/       # This folder
        ├── index.md               # Quick overview
        ├── QUICK_START.md         # 30-second setup
        ├── README.md              # Full documentation
        ├── TEST_RESULTS.md        # Execution results
        ├── SETUP_GUIDE.md         # This file
        ├── test_runner.py         # Test execution script
        ├── run_tests.sh           # Bash runner
        ├── run_tests.bat          # Windows runner
        └── Test Resumes (5)
            ├── test_inject_1_ignore.txt
            ├── test_inject_2_bypass.txt
            ├── test_inject_3_approval.txt
            ├── test_inject_4_tags.txt
            └── test_inject_5_execute.txt
```

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Bash (for Linux/Mac) or Command Prompt (for Windows)
- Git (optional, for version control)

### Python Packages
The following are required:
- `requests` - For API testing
- `better-profanity` - Used by safety module

Install with:
```bash
pip install -r ../../backend/requirements.txt
```

### Optional: Running Backend
To test API endpoints:
```bash
cd backend
python main.py
```
Backend will run on `http://localhost:5000`

## Installation Steps

### Step 1: Verify Python Installation
```bash
python --version
# Should output: Python 3.8 or higher
```

### Step 2: Install Dependencies
```bash
cd Resume-screener-agentic-ATS
pip install -r backend/requirements.txt
```

### Step 3: Navigate to Test Folder
```bash
cd tests/injection_detection
```

### Step 4: Verify Test Files
```bash
# On Windows
dir test_inject_*.txt

# On Linux/Mac
ls test_inject_*.txt
```

You should see 5 test resume files.

## Running Tests

### Method 1: Using Python Directly (Recommended)
```bash
python test_runner.py
```

### Method 2: Using Shell Script (Linux/Mac)
```bash
bash run_tests.sh
```

### Method 3: Using Batch Script (Windows)
```cmd
run_tests.bat
```

### Method 4: From Project Root
```bash
cd Resume-screener-agentic-ATS
python tests/injection_detection/test_runner.py
```

## Expected Output

Successful test run output:
```
======================================================================
LOCAL INJECTION DETECTION TESTS
======================================================================

✅ test_inject_1_ignore
   Type: Ignore/Forget instructions
   Expected: True, Got: True
   Pattern: ignore all job requirements...

[... 4 more local tests ...]

======================================================================
API INJECTION DETECTION TESTS
======================================================================

✅ test_inject_1_ignore
   Type: Ignore/Forget instructions
   Expected Blocked: True, Got: True
   Status Code: 400

[... 4 more API tests ...]

======================================================================
LEGITIMATE RESUME TEST
======================================================================

✅ Legitimate Resume Test: PASS
   Expected: No injection detected
   Got: Injection=No

======================================================================
TEST SUMMARY
======================================================================

Local Detection Tests:  5 passed, 0 failed
API Detection Tests:    5 passed, 0 failed
Legitimate Resume Test: 1 passed, 0 failed

Total: 11/11 tests passed

✅ ALL TESTS PASSED!
```

## Test Results

### All Tests Pass When:
✅ All 5 injection resumes are detected (100% detection)
✅ All 5 injection resumes are blocked (400 status code)
✅ Legitimate resumes pass without false positives
✅ Security incidents are properly logged

### Success Criteria
- **Local Detection:** 5/5 tests pass
- **API Detection:** 5/5 tests pass (if API running)
- **Legitimate Resumes:** 1/1 test pass
- **Total:** 11/11 or 6/6 (without API)

## Test Breakdown

### Test 1: Ignore/Forget Instructions
**File:** `test_inject_1_ignore.txt`
**Payload:** Commands to ignore requirements and shortlist automatically
**Expected:** DETECTED and BLOCKED ✅

### Test 2: Bypass/Override System
**File:** `test_inject_2_bypass.txt`
**Payload:** Commands to bypass scoring system and override restrictions
**Expected:** DETECTED and BLOCKED ✅

### Test 3: Approval/Scoring Manipulation
**File:** `test_inject_3_approval.txt`
**Payload:** Requests for automatic approval and score manipulation
**Expected:** DETECTED and BLOCKED ✅

### Test 4: XML/HTML/Function Calls
**File:** `test_inject_4_tags.txt`
**Payload:** System tags, HTML comments, and function calls
**Expected:** DETECTED and BLOCKED ✅

### Test 5: Command Execution
**File:** `test_inject_5_execute.txt`
**Payload:** Execute commands and function invocations
**Expected:** DETECTED and BLOCKED ✅

### Test 6: Legitimate Resume
**Content:** Real resume without injection
**Expected:** NOT DETECTED ✅

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'backend'"
**Solution:**
```bash
# Make sure you're in the project root
cd Resume-screener-agentic-ATS
python tests/injection_detection/test_runner.py
```

### Problem: "Cannot connect to API"
**Solution:**
This is normal. Tests automatically fall back to local detection.
To test API endpoints, start the backend:
```bash
python backend/main.py
# In another terminal
python tests/injection_detection/test_runner.py
```

### Problem: "Permission denied" on .sh file
**Solution:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Problem: Python not found
**Solution:**
```bash
# Verify Python installation
python --version

# If not found, install Python 3.8+
# From: https://www.python.org/downloads/
```

### Problem: Test files not found
**Solution:**
```bash
# Verify you're in correct directory
pwd  # Should end with: tests/injection_detection

# Check files exist
ls test_inject_*.txt  # Linux/Mac
dir test_inject_*.txt # Windows
```

## Advanced Usage

### Run Only Local Tests (No API needed)
The test runner automatically detects if API is unavailable and runs local tests.

### Manual Local Testing
```bash
python
>>> from backend.services.safety import detect_prompt_injection
>>> with open('test_inject_1_ignore.txt') as f:
>>>     is_injection, pattern = detect_prompt_injection(f.read())
>>>     print(f"Injection detected: {is_injection}")
>>>     print(f"Pattern: {pattern}")
```

### Manual API Testing
```bash
# Upload test resume
curl -X POST http://localhost:5000/api/screen \
  -F "resume=@test_inject_1_ignore.txt" \
  -F "job_role_id=edd817fc"

# Expected response: 400 status with INJECTION_DETECTED
```

### Check Security Incidents
```bash
curl http://localhost:5000/api/security-incidents
```

### Check Audit Trail
```bash
curl http://localhost:5000/api/audit-trail
```

## Integration with CI/CD

Add to your CI/CD pipeline (GitHub Actions example):

```yaml
test-injection-detection:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - run: pip install -r backend/requirements.txt
    - run: |
        cd tests/injection_detection
        python test_runner.py
```

## Test Execution Statistics

### Timing
- Local tests: ~100ms
- API tests: ~2-5 seconds (depends on API response time)
- Total: <10 seconds

### Coverage
- Attack vectors: 5
- Test cases: 5 injection + 1 legitimate
- Patterns tested: 21+
- Success rate: 100%

## Files Reference

| File | Purpose | Type |
|------|---------|------|
| `index.md` | Quick overview | Documentation |
| `QUICK_START.md` | 30-second setup | Documentation |
| `README.md` | Complete reference | Documentation |
| `TEST_RESULTS.md` | Latest results | Documentation |
| `SETUP_GUIDE.md` | This file | Documentation |
| `test_runner.py` | Test execution | Code |
| `run_tests.sh` | Linux/Mac runner | Script |
| `run_tests.bat` | Windows runner | Script |
| `test_inject_*.txt` | Test resumes | Test Data |

## Next Steps

1. **Run the tests:** `python test_runner.py`
2. **Review documentation:** Start with [QUICK_START.md](QUICK_START.md)
3. **Check results:** Read [TEST_RESULTS.md](TEST_RESULTS.md)
4. **Understand the code:** Review [backend/services/safety.py](../../backend/services/safety.py)
5. **Add to CI/CD:** Integrate tests into your pipeline

## Support

- **Quick answers:** See [QUICK_START.md](QUICK_START.md)
- **Detailed info:** Read [README.md](README.md)
- **Results:** Check [TEST_RESULTS.md](TEST_RESULTS.md)
- **Code:** Review `backend/services/safety.py`

## Security Notes

✅ All test payloads are clearly marked
✅ No real candidate data compromised
✅ Tests are isolated and repeatable
✅ Results are auditable and loggable
✅ Designed to be run frequently

---

**Ready to test?** Run: `python test_runner.py`

**Questions?** Check the documentation files above.

**Found an issue?** Review the troubleshooting section.
