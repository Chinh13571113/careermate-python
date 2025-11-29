"""
Quick Demo: Free-text Input Support

This demonstrates that the system ALREADY supports free-form text input!
You don't need to provide structured skills - just write naturally.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")

def print_result(response_data):
    """Pretty print the response"""
    if response_data.get('success'):
        print("✓ SUCCESS!\n")
        
        if 'input_type' in response_data and response_data['input_type'] == 'free_text':
            print(f"📝 Input Type: FREE-FORM TEXT")
            print(f"🔍 Extracted Skills: {', '.join(response_data.get('extracted_skills', []))}")
            print(f"📅 Extracted Experience: {response_data.get('extracted_experience', 0)} years")
            
            confidence = response_data.get('confidence_metrics', {})
            print(f"\n📊 Extraction Confidence:")
            print(f"   - Overall: {confidence.get('overall_confidence', 0):.1%}")
            print(f"   - Skills found: {confidence.get('skill_confidence', 0):.1%}")
            print(f"   - Experience found: {confidence.get('experience_confidence', 0):.1%}")
        
        print(f"\n🎯 Top Recommendations:")
        for i, rec in enumerate(response_data.get('recommendations', [])[:3], 1):
            print(f"\n   {i}. {rec['position']}")
            print(f"      Confidence: {rec['confidence']:.2f} ({rec['confidence']*100:.0f}%)")
            print(f"      Matching Skills: {', '.join(rec['matching_skills'][:5])}")
    else:
        print(f"✗ ERROR: {response_data.get('error')}")


def test_free_text_input():
    """Test 1: Free-form text input (natural language)"""
    print_header("TEST 1: FREE-FORM TEXT INPUT")
    
    # Natural language input - just like a user would type
    free_text = """
    I'm a software developer with 5 years of experience. 
    I've been working with Python and Django for web development.
    I also know JavaScript, React, and have experience with PostgreSQL databases.
    Recently I've been learning Docker and AWS for deployment.
    """
    
    print(f"📝 User Input (natural text):")
    print(f"{free_text.strip()}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cv-creation/recommend-roles/",
            json={"text": free_text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_result(response.json())
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to server. Is Django running?")
        print("   Start server: python manage.py runserver")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")


def test_structured_input():
    """Test 2: Structured input (original format)"""
    print_header("TEST 2: STRUCTURED INPUT (Original Format)")
    
    data = {
        "skills": ["Python", "Django", "React", "PostgreSQL", "Docker"],
        "experience_years": 5
    }
    
    print(f"📋 Structured Input:")
    print(json.dumps(data, indent=2))
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cv-creation/recommend-roles/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_result(response.json())
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to server. Is Django running?")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")


def test_conversational_input():
    """Test 3: Very conversational/casual input"""
    print_header("TEST 3: CASUAL CONVERSATIONAL INPUT")
    
    casual_text = """
    Hey! So I've been coding for about 3 years now, mostly backend stuff.
    I really love working with Python, it's my main language.
    I use Django a lot for building APIs and web apps.
    Oh, and I know some SQL too - mostly PostgreSQL.
    I'm trying to learn more about cloud stuff like AWS.
    """
    
    print(f"💬 Casual Input:")
    print(f"{casual_text.strip()}\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/cv-creation/recommend-roles/",
            json={"text": casual_text},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_result(response.json())
        else:
            print(f"✗ Error: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to server. Is Django running?")
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")


def show_swagger_info():
    """Show how to access Swagger UI"""
    print_header("SWAGGER API DOCUMENTATION")
    
    print("📚 Your API already has Swagger UI available!\n")
    print("🌐 Access it at: http://localhost:8000/swagger/")
    print()
    print("Features:")
    print("  ✓ Interactive API testing")
    print("  ✓ Try out endpoints directly in browser")
    print("  ✓ See request/response formats")
    print("  ✓ View all available endpoints")
    print()
    print("Available endpoints:")
    print("  • POST /api/cv-creation/recommend-roles/")
    print("  • POST /api/cv-creation/skill-insights/")
    print("  • GET  /api/cv-creation/available-roles/")
    print("  • GET  /api/cv-creation/health/")
    print()
    print("To test free-text input in Swagger:")
    print('  1. Open http://localhost:8000/swagger/')
    print('  2. Click on "POST /api/cv-creation/recommend-roles/"')
    print('  3. Click "Try it out"')
    print('  4. Enter JSON: {"text": "I have 5 years of Python experience"}')
    print('  5. Click "Execute"')
    print()


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("FREE-TEXT INPUT DEMO - Career Recommendation System".center(80))
    print("="*80)
    print("\nYour system ALREADY supports free-form text input!")
    print("Users can type naturally - no need for structured skills list.")
    print()
    
    # Show Swagger info
    show_swagger_info()
    
    # Run tests
    test_free_text_input()
    test_conversational_input()
    test_structured_input()
    
    # Final summary
    print_header("SUMMARY")
    print("✅ Your system supports BOTH input formats:")
    print()
    print("1️⃣  FREE-FORM TEXT (Natural Language)")
    print('   Request: {"text": "I have 5 years Python experience..."}')
    print("   → System extracts skills and experience automatically")
    print()
    print("2️⃣  STRUCTURED INPUT (Original)")
    print('   Request: {"skills": ["Python", "Django"], "experience_years": 5}')
    print("   → Direct skill matching")
    print()
    print("🔧 Testing Tools:")
    print("   • Swagger UI: http://localhost:8000/swagger/")
    print("   • This script: python quick_test_free_text.py")
    print("   • curl commands (see documentation)")
    print()
    print("📖 Full documentation: DEVELOPMENT_GUIDE.md")
    print()


if __name__ == "__main__":
    main()
