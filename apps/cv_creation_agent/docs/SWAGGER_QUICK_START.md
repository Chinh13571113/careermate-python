# 🚀 Quick Swagger Test Guide

## ⚠️ You Got a 403 Error? That's Normal!

The `/api/test/` endpoint requires authentication. **Use these endpoints instead:**

---

## ✅ Working Endpoints (No Authentication Required)

### 🎯 Best Endpoint to Try First

**`POST /api/cv-creation/recommend-roles/`**

This is your main endpoint - works with both formats!

---

## 📝 Step-by-Step Test in Swagger

### Step 1: Open Swagger
```
http://localhost:8000/swagger/
```

### Step 2: Find the Right Endpoint
- ❌ **SKIP** `/api/test/` (requires auth - gives 403)
- ✅ **USE** `/api/cv-creation/recommend-roles/`

### Step 3: Click "Try it out"
Button is on the right side of the endpoint

### Step 4: Enter Test Data

**Option A: Free-Form Text** (Natural Language)
```json
{
  "text": "I'm a developer with 5 years Python and Django experience"
}
```

**Option B: Structured Input**
```json
{
  "skills": ["Python", "Django", "PostgreSQL"],
  "experience_years": 5
}
```

### Step 5: Click "Execute"

### Step 6: See Results! 🎉
You should see:
- ✅ Status code: 200
- ✅ Response with recommendations
- ✅ Confidence scores
- ✅ Matching skills

---

## 🧪 All Working Endpoints to Test

### 1. POST /api/cv-creation/recommend-roles/
**What it does**: Gets career recommendations

**Test with**:
```json
{
  "text": "Full stack developer with 3 years experience. Python, React, PostgreSQL."
}
```

**Expected**: 200 OK with recommendations

---

### 2. POST /api/cv-creation/skill-insights/
**What it does**: Analyzes your skill profile

**Test with**:
```json
{
  "skills": ["Python", "React", "Docker", "PostgreSQL"]
}
```

**Expected**: 200 OK with skill analysis (full-stack, backend focus, etc.)

---

### 3. GET /api/cv-creation/available-roles/
**What it does**: Lists all 12 available roles

**Test with**: Nothing! Just click "Execute"

**Expected**: 200 OK with list of all roles

---

### 4. GET /api/cv-creation/health/
**What it does**: Checks if system is working

**Test with**: Nothing! Just click "Execute"

**Expected**: 
```json
{
  "success": true,
  "status": "healthy",
  "recommender_loaded": true,
  "skill_extractor_loaded": true
}
```

---

## 🎯 Quick Test Right Now!

### Copy-Paste This Into Swagger:

```json
{
  "text": "I'm a software engineer with 7 years of experience. I specialize in Python, Django, Flask, PostgreSQL, Redis, Docker, and Kubernetes. I've built REST APIs and microservices."
}
```

**What you'll see**:
```json
{
  "success": true,
  "input_type": "free_text",
  "extracted_skills": ["Python", "Django", "Flask", "PostgreSQL", "Redis", "Docker", "Kubernetes"],
  "extracted_experience": 7.0,
  "recommendations": [
    {
      "role": "Backend Developer",
      "position": "Senior Backend Developer",
      "confidence": 1.00,
      "matching_skills": ["Python", "Django", "Flask", "PostgreSQL", "Redis", "Docker", "Kubernetes"]
    }
  ]
}
```

---

## ❌ Don't Test These (They Need Auth)

- `/api/test/` → 403 Forbidden ❌
- Any endpoint with a 🔒 lock icon

---

## 💡 Pro Tips

1. **Start with `/health/`** - confirms system is working
2. **Then try `/recommend-roles/`** with free-text input
3. **Check `/available-roles/`** - see what roles exist
4. **Use real examples** - makes testing more interesting!

---

## 🎉 Success Checklist

After testing in Swagger, you should have:

- ✅ Tested health check (200 OK)
- ✅ Got recommendations from free-text input (200 OK)
- ✅ Saw skill extraction working (skills + experience detected)
- ✅ Received confidence scores (0.0 - 1.0)
- ✅ Got matching and suggested skills

---

## 🆘 Still Getting Errors?

### Error: "Authentication credentials were not provided"
→ You're testing the wrong endpoint! Use `/api/cv-creation/` endpoints

### Error: "Could not extract any skills from text"
→ Make sure to mention specific technologies (Python, JavaScript, etc.)

### Error: "Skills are required"
→ Check JSON format - needs either `"text"` or `"skills"` field

### Error: Connection refused
→ Django server not running. Start it: `python manage.py runserver`

---

**Ready? Go to http://localhost:8000/swagger/ and test the endpoints!** 🚀
