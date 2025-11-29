"""
Test script for CV Analysis API with rate limit optimization
Tests:
1. First call - should work (cache miss)
2. Second immediate call - should use cache and not count against quota
3. Rate limit enforcement
"""

import requests
import time
import os

API_URL = "http://localhost:8000/api/v1/cv/analyze-ats/"

# Sample test data
TEST_CV_PATH = r"D:\FPT_Uni\Fall 2025\be-python\agent_core\data\LE-QUANG-ANH-TopCV.vn-131025.213322.pdf"
TEST_JD = """
We are looking for a Senior Python Developer with:
- 5+ years of Python experience
- Django, FastAPI, Flask
- PostgreSQL, Redis
- Docker, Kubernetes
- REST API design
- AWS or GCP experience
"""

def test_cv_analysis():
    print("🧪 Testing CV Analysis API with Rate Limit Optimization\n")
    print("=" * 60)

    # Check if test CV file exists
    if not os.path.exists(TEST_CV_PATH):
        print(f"❌ Test CV file not found: {TEST_CV_PATH}")
        print("Please update TEST_CV_PATH with a valid PDF file")
        return

    # Test 1: First call (should work - cache miss)
    print("\n📤 Test 1: First API call (cache miss expected)")
    print("-" * 60)

    with open(TEST_CV_PATH, 'rb') as cv_file:
        files = {'cv_file': cv_file}
        data = {'job_description': TEST_JD}

        start = time.time()
        response = requests.post(API_URL, files=files, data=data)
        elapsed = time.time() - start

    print(f"Status: {response.status_code}")
    print(f"Time: {elapsed:.2f}s")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"Overall Score: {result.get('overall_score', 'N/A')}")

        # Check cache info
        cache_info = result.get('cache', {})
        rate_limit = result.get('rate_limit', {})

        print(f"\n📊 Cache Info:")
        print(f"  - Cache Hit: {cache_info.get('hit', False)}")
        print(f"  - Cache Key: {cache_info.get('key', 'N/A')[:16]}...")

        print(f"\n🔒 Rate Limit Info:")
        print(f"  - Plan: {rate_limit.get('plan', 'N/A')}")
        print(f"  - Cached: {rate_limit.get('cached', False)}")
        print(f"  - Quota Used: {rate_limit.get('quota_used', 'N/A')}")
        print(f"  - Remaining Today: {rate_limit.get('remaining_today', 'N/A')}")

        cache_key = cache_info.get('key')
    else:
        print(f"❌ Failed: {response.text}")
        return

    # Test 2: Immediate second call (should use cache)
    print("\n" + "=" * 60)
    print("📤 Test 2: Immediate second call (cache hit expected)")
    print("-" * 60)

    with open(TEST_CV_PATH, 'rb') as cv_file:
        files = {'cv_file': cv_file}
        data = {'job_description': TEST_JD}

        start = time.time()
        response = requests.post(API_URL, files=files, data=data)
        elapsed = time.time() - start

    print(f"Status: {response.status_code}")
    print(f"Time: {elapsed:.2f}s")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")

        cache_info = result.get('cache', {})
        rate_limit = result.get('rate_limit', {})

        print(f"\n📊 Cache Info:")
        print(f"  - Cache Hit: {cache_info.get('hit', False)} {'✅' if cache_info.get('hit') else '❌'}")
        print(f"  - Age: {cache_info.get('age_seconds', 'N/A')}s")

        print(f"\n🔒 Rate Limit Info:")
        print(f"  - Cached: {rate_limit.get('cached', False)} {'✅' if rate_limit.get('cached') else '❌'}")
        print(f"  - Quota Used: {rate_limit.get('quota_used', 'N/A')}")
        print(f"  - Remaining Today: {rate_limit.get('remaining_today', 'N/A')}")

        if cache_info.get('hit') and not rate_limit.get('quota_used'):
            print("\n🎉 PERFECT! Cache hit and quota not consumed!")
        else:
            print("\n⚠️ Cache might not be working as expected")
    else:
        print(f"❌ Failed: {response.text}")

    # Test 3: Third call with different JD (should trigger rate limit or succeed)
    print("\n" + "=" * 60)
    print("📤 Test 3: Call with different JD (should wait or use new quota)")
    print("-" * 60)
    print("⏳ Waiting 2 seconds...")
    time.sleep(2)

    DIFFERENT_JD = """
    Looking for a Frontend Developer:
    - React, Vue.js
    - TypeScript
    - CSS, HTML5
    - Responsive design
    """

    with open(TEST_CV_PATH, 'rb') as cv_file:
        files = {'cv_file': cv_file}
        data = {'job_description': DIFFERENT_JD}

        start = time.time()
        response = requests.post(API_URL, files=files, data=data)
        elapsed = time.time() - start

    print(f"Status: {response.status_code}")
    print(f"Time: {elapsed:.2f}s")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        rate_limit = result.get('rate_limit', {})
        print(f"\n🔒 Rate Limit Info:")
        print(f"  - Remaining Today: {rate_limit.get('remaining_today', 'N/A')}")
    elif response.status_code == 429:
        result = response.json()
        print(f"⏱️ Rate limited (expected if interval < 10s)")
        print(f"  - Retry after: {result.get('retry_after', 'N/A')}s")
        print(f"  - Reason: {result.get('reason', 'N/A')}")
        print(f"  - Tip: {result.get('tip', 'N/A')}")
    else:
        print(f"❌ Failed: {response.text}")

    print("\n" + "=" * 60)
    print("✅ Tests completed!")
    print("\n💡 Key improvements:")
    print("  1. FREE plan: 10 requests/day (was 5)")
    print("  2. Interval: 10s between requests (was 30s)")
    print("  3. Cache hits don't consume quota")
    print("  4. Cache TTL: 7 days")

if __name__ == "__main__":
    test_cv_analysis()

