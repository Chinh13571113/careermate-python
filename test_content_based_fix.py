"""
Test Content-Based Recommender sau khi fix
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Careermate.settings')
django.setup()

import asyncio
from apps.recommendation_agent.services.content_based_recommender import get_content_based_recommendations

async def test_backend_developer():
    """Test case: Backend Developer với Python skills"""
    print("\n" + "🚀 " * 40)
    print("TEST CASE: Backend Developer với Python/Django skills")
    print("🚀 " * 40)
    
    query_item = {
        "title": "Backend Developer",
        "skills": ["java", "nextjs", "sql", "pytorch", "Python", "pandas", "numpy"],
        "description": "Looking for backend developer position with Python experience"
    }
    
    results = await get_content_based_recommendations(query_item, top_n=5)
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS (Top 5)")
    print("=" * 80)
    
    for i, job in enumerate(results, 1):
        match_pct = job['similarity'] * 100
        semantic_pct = job['semantic_similarity'] * 100
        skill_pct = job['skill_overlap'] * 100
        
        print(f"\n{i}. {job['title']} (ID: {job['job_id']})")
        print(f"   ⭐ Match: {match_pct:.1f}%")
        print(f"   🧠 Semantic: {semantic_pct:.1f}%")
        print(f"   🎯 Skill: {skill_pct:.1f}%")
        print(f"   📈 Title Boost: {job['title_boost']*100:.1f}%")
        print(f"   Skills: {job['skills'][:100]}...")
        
        # Validate logic
        expected_base = 0.5 * job['semantic_similarity'] + 0.5 * job['skill_overlap']
        if job['skill_overlap'] > 0:
            expected_final = expected_base + job['title_boost']
        else:
            expected_final = expected_base * 0.5
        
        if abs(job['similarity'] - expected_final) < 0.01:
            print(f"   ✅ Score calculation correct!")
        else:
            print(f"   ❌ Score mismatch! Expected: {expected_final:.4f}, Got: {job['similarity']:.4f}")

async def test_python_developer():
    """Test case: Python Developer - không được recommend Java jobs"""
    print("\n\n" + "🐍 " * 40)
    print("TEST CASE: Python Developer (should NOT recommend Java jobs)")
    print("🐍 " * 40)
    
    query_item = {
        "title": "Python Developer",
        "skills": ["Python", "Django", "Flask", "FastAPI", "PostgreSQL"],
        "description": "Python backend developer"
    }
    
    results = await get_content_based_recommendations(query_item, top_n=5)
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS (Top 5)")
    print("=" * 80)
    
    java_found = False
    for i, job in enumerate(results, 1):
        match_pct = job['similarity'] * 100
        skill_pct = job['skill_overlap'] * 100
        
        print(f"\n{i}. {job['title']} (ID: {job['job_id']})")
        print(f"   Match: {match_pct:.1f}%, Skill: {skill_pct:.1f}%")
        
        # Check if Java job leaked in
        if 'java' in job['title'].lower() and 'javascript' not in job['title'].lower():
            java_found = True
            print(f"   ⚠️  WARNING: Java job in Python results!")
    
    if not java_found:
        print(f"\n✅ Test PASSED: No Java jobs recommended for Python developer")
    else:
        print(f"\n❌ Test FAILED: Java jobs still appearing!")

async def test_nodejs_developer():
    """Test case: Node.js Developer"""
    print("\n\n" + "🟢 " * 40)
    print("TEST CASE: Node.js Developer")
    print("🟢 " * 40)
    
    query_item = {
        "title": "Backend Node.js Developer",
        "skills": ["Node.js", "Express", "TypeScript", "MongoDB"],
        "description": "Node.js backend developer"
    }
    
    results = await get_content_based_recommendations(query_item, top_n=5)
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS (Top 5)")
    print("=" * 80)
    
    for i, job in enumerate(results, 1):
        match_pct = job['similarity'] * 100
        skill_pct = job['skill_overlap'] * 100
        
        print(f"{i}. {job['title']}: Match {match_pct:.1f}%, Skill {skill_pct:.1f}%")

async def main():
    await test_backend_developer()
    await test_python_developer()
    await test_nodejs_developer()
    
    print("\n\n" + "=" * 80)
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
