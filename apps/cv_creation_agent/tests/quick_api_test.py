"""
Quick API Test Script

Tests both free-form and structured input formats
Run this after starting the Django server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def test_health():
    """Test health endpoint"""
    print(f"\n{Colors.BOLD}Testing Health Endpoint...{Colors.RESET}")
    try:
        response = requests.get(f"{BASE_URL}/api/cv-creation/health/")
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✓ Server is healthy{Colors.RESET}")
            print(f"  Recommender loaded: {data.get('recommender_loaded')}")
            print(f"  Skill extractor loaded: {data.get('skill_extractor_loaded')}")
            return True
        else:
            print(f"{Colors.RED}✗ Health check failed: {response.status_code}{Colors.RESET}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ Cannot connect to server. Is it running?{Colors.RESET}")
        print(f"{Colors.YELLOW}  Start with: python manage.py runserver{Colors.RESET}")
        return False

def test_free_form_input():
    """Test free-form text input"""
    print(f"\n{Colors.BOLD}Testing Free-Form Text Input...{Colors.RESET}")
    
    payload = {
        "text": "I'm a backend developer with 5 years of experience. I work with Python, Django, PostgreSQL, and Docker."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cv-creation/recommend-roles/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✓ Free-form input working!{Colors.RESET}")
            print(f"\n  Input type: {data.get('input_type')}")
            print(f"  Extracted skills: {', '.join(data.get('extracted_skills', []))}")
            print(f"  Extracted experience: {data.get('extracted_experience')} years")
            print(f"  Extraction quality: {data.get('confidence_metrics', {}).get('extraction_quality')}")
            
            recommendations = data.get('recommendations', [])
            if recommendations:
                print(f"\n  Top Recommendation:")
                top = recommendations[0]
                print(f"    → {top['position']} (confidence: {top['confidence']:.2f})")
            return True
        else:
            print(f"{Colors.RED}✗ Request failed: {response.status_code}{Colors.RESET}")
            print(f"  {response.text}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return False

def test_structured_input():
    """Test structured JSON input"""
    print(f"\n{Colors.BOLD}Testing Structured Input...{Colors.RESET}")
    
    payload = {
        "skills": ["Python", "Django", "PostgreSQL", "Docker"],
        "experience_years": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cv-creation/recommend-roles/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✓ Structured input working!{Colors.RESET}")
            print(f"\n  Input type: {data.get('input_type')}")
            print(f"  Skills: {', '.join(payload['skills'])}")
            print(f"  Experience: {payload['experience_years']} years")
            
            recommendations = data.get('recommendations', [])
            if recommendations:
                print(f"\n  Top Recommendation:")
                top = recommendations[0]
                print(f"    → {top['position']} (confidence: {top['confidence']:.2f})")
            return True
        else:
            print(f"{Colors.RED}✗ Request failed: {response.status_code}{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return False

def test_skill_extraction():
    """Test skill extraction endpoint"""
    print(f"\n{Colors.BOLD}Testing Skill Extraction Endpoint...{Colors.RESET}")
    
    payload = {
        "text": "Full stack developer with 3 years experience in React, Node.js, and MongoDB."
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cv-creation/extract-skills/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.GREEN}✓ Extraction endpoint working!{Colors.RESET}")
            print(f"\n  Extracted skills: {', '.join(data.get('extracted_skills', []))}")
            print(f"  Extracted experience: {data.get('extracted_experience')} years")
            print(f"  Quality: {data.get('confidence_metrics', {}).get('extraction_quality')}")
            return True
        else:
            print(f"{Colors.RED}✗ Request failed: {response.status_code}{Colors.RESET}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return False

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           API Quick Test - Free-Form Text Input           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print(f"\n{Colors.YELLOW}Cannot proceed without server running.{Colors.RESET}")
        print(f"{Colors.YELLOW}Start server with: python manage.py runserver{Colors.RESET}")
        return
    
    # Test 2: Free-form input
    results.append(("Free-Form Input", test_free_form_input()))
    
    # Test 3: Structured input
    results.append(("Structured Input", test_structured_input()))
    
    # Test 4: Skill extraction
    results.append(("Skill Extraction", test_skill_extraction()))
    
    # Summary
    print(f"\n{Colors.BOLD}Test Summary:{Colors.RESET}")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {status}: {test_name}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! System is ready.{Colors.RESET}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
        print(f"  1. Open Swagger UI: {Colors.BLUE}http://localhost:8000/swagger/{Colors.RESET}")
        print(f"  2. Try the endpoints with your own text!")
    else:
        print(f"\n{Colors.YELLOW}Some tests failed. Check the errors above.{Colors.RESET}")

if __name__ == "__main__":
    main()
