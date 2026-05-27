"""
Prompt Injection Detection Test Runner
Tests the injection detection system against various payload styles
"""

import os
import sys
import requests
import json
from pathlib import Path
import io

# Handle emoji output on Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.safety import detect_prompt_injection

# Test configuration
TEST_DIR = Path(__file__).parent
API_BASE = "http://localhost:5000"
ROLE_ID = "edd817fc"  # UX/UI Designer role

test_cases = [
    {
        "name": "test_inject_1_ignore",
        "file": "test_inject_1_ignore.txt",
        "expected_detected": True,
        "payload_type": "Ignore/Forget instructions"
    },
    {
        "name": "test_inject_2_bypass",
        "file": "test_inject_2_bypass.txt",
        "expected_detected": True,
        "payload_type": "Bypass/Override system"
    },
    {
        "name": "test_inject_3_approval",
        "file": "test_inject_3_approval.txt",
        "expected_detected": True,
        "payload_type": "Approval/Scoring manipulation"
    },
    {
        "name": "test_inject_4_tags",
        "file": "test_inject_4_tags.txt",
        "expected_detected": True,
        "payload_type": "XML/HTML tags and function calls"
    },
    {
        "name": "test_inject_5_execute",
        "file": "test_inject_5_execute.txt",
        "expected_detected": True,
        "payload_type": "Execute command injection"
    },
]

def test_local_detection():
    """Test injection detection locally without API call"""
    print("\n" + "="*70)
    print("LOCAL INJECTION DETECTION TESTS")
    print("="*70)

    passed = 0
    failed = 0

    for test in test_cases:
        filepath = TEST_DIR / test["file"]
        if not filepath.exists():
            print(f"\n❌ {test['name']}: File not found at {filepath}")
            failed += 1
            continue

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            resume_text = f.read()

        is_injection, pattern = detect_prompt_injection(resume_text)

        expected = test["expected_detected"]
        status = "✅" if is_injection == expected else "❌"
        passed += 1 if is_injection == expected else 0
        failed += 0 if is_injection == expected else 1

        print(f"\n{status} {test['name']}")
        print(f"   Type: {test['payload_type']}")
        print(f"   Expected: {expected}, Got: {is_injection}")
        if pattern:
            print(f"   Pattern: {pattern[:60]}..." if len(pattern) > 60 else f"   Pattern: {pattern}")

    return passed, failed

def test_api_detection():
    """Test injection detection through API"""
    print("\n" + "="*70)
    print("API INJECTION DETECTION TESTS")
    print("="*70)

    try:
        # Check if API is running
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code != 200:
            print(f"\n[!] API health check failed. Skipping API tests.")
            return 0, 0
    except (requests.ConnectionError, requests.Timeout):
        print(f"\n[!] Cannot connect to API at {API_BASE}. Skipping API tests.")
        return 0, 0
    except Exception as e:
        print(f"\n[!] API check failed ({str(e)}). Skipping API tests.")
        return 0, 0

    passed = 0
    failed = 0

    for test in test_cases:
        filepath = TEST_DIR / test["file"]
        if not filepath.exists():
            print(f"\n❌ {test['name']}: File not found")
            failed += 1
            continue

        try:
            with open(filepath, 'rb') as f:
                files = {'resume': (test["file"], f)}
                data = {'job_role_id': ROLE_ID}
                response = requests.post(
                    f"{API_BASE}/api/screen",
                    files=files,
                    data=data,
                    timeout=10
                )

            # Injection should cause 400 error with INJECTION_DETECTED code and malware feedback
            is_blocked = response.status_code == 400
            has_injection_code = "INJECTION_DETECTED" in response.text
            has_malware_feedback = "malware_feedback" in response.text
            injection_detected = is_blocked and has_injection_code and has_malware_feedback

            expected = test["expected_detected"]
            status = "✅" if injection_detected == expected else "❌"
            passed += 1 if injection_detected == expected else 0
            failed += 0 if injection_detected == expected else 1

            print(f"\n{status} {test['name']}")
            print(f"   Type: {test['payload_type']}")
            print(f"   Expected Blocked: {expected}, Got: {injection_detected}")
            print(f"   Status Code: {response.status_code}")

            if injection_detected:
                response_json = response.json()
                if "detected_pattern" in response_json:
                    pattern = response_json["detected_pattern"]
                    print(f"   Pattern: {pattern[:60]}..." if len(pattern) > 60 else f"   Pattern: {pattern}")

        except Exception as e:
            print(f"\n❌ {test['name']}: API request failed - {str(e)}")
            failed += 1

    return passed, failed

def test_legitimate_resume():
    """Test that legitimate resumes pass through"""
    print("\n" + "="*70)
    print("LEGITIMATE RESUME TEST")
    print("="*70)

    legitimate_resume = """
JOHN SMITH
San Francisco, CA | john.smith@email.com | (415) 555-0100

PROFESSIONAL SUMMARY
UI/UX Designer with 6 years of experience in digital product design.

TECHNICAL SKILLS
Tools: Figma, Adobe XD, Sketch
Skills: User Research, Interaction Design

PROFESSIONAL EXPERIENCE

Senior UX Designer | TechCorp | Jan 2022 - Present
- Led user research studies with 50+ participants
- Designed interaction patterns used by 100k+ users

EDUCATION
Bachelor of Arts in Graphic Design | California State University | 2018
"""

    is_injection, pattern = detect_prompt_injection(legitimate_resume)

    status = "✅" if not is_injection else "❌"
    result = "PASS" if not is_injection else "FAIL"

    print(f"\n{status} Legitimate Resume Test: {result}")
    print(f"   Expected: No injection detected")
    print(f"   Got: Injection={'Yes' if is_injection else 'No'}")

    return (1, 0) if not is_injection else (0, 1)

def print_summary(local_p, local_f, api_p, api_f, legit_p, legit_f):
    """Print test summary"""
    total_p = local_p + api_p + legit_p
    total_f = local_f + api_f + legit_f
    total = total_p + total_f

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"\nLocal Detection Tests:  {local_p} passed, {local_f} failed")
    print(f"API Detection Tests:    {api_p} passed, {api_f} failed")
    print(f"Legitimate Resume Test: {legit_p} passed, {legit_f} failed")
    print(f"\nTotal: {total_p}/{total} tests passed")

    if total_f == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ {total_f} test(s) failed")

    return total_f == 0

if __name__ == "__main__":
    print("\nPrompt Injection Detection Test Suite")
    print("="*70)

    # Run tests
    local_p, local_f = test_local_detection()
    api_p, api_f = test_api_detection()
    legit_p, legit_f = test_legitimate_resume()

    # Print summary
    success = print_summary(local_p, local_f, api_p, api_f, legit_p, legit_f)

    sys.exit(0 if success else 1)
