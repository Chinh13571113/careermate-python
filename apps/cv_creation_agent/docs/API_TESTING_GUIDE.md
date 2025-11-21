# API Testing Guide - Career Recommendation System

## 🎉 Great News: Your System Already Supports Both!

### ✅ **1. FREE-FORM TEXT INPUT** (Natural Language) - Users can type naturally!
### ✅ **2. SWAGGER UI** (Interactive API Testing) - Test in your browser!

**Quick Start**: Access Swagger UI at `http://localhost:8000/swagger/`

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd "d:\SEP490\BE PY\be-python"
python manage.py runserver
```

### 2. Access Swagger UI
Open your browser and go to:
```
http://localhost:8000/swagger/
```

⚠️ **Important**: The `/api/test/` endpoint requires authentication (403 error is normal).  
✅ **Use these endpoints instead** - they work without authentication!

### 3. Test Free-Text Input in Swagger (No Auth Required!)

#### Option A: Test with Free-Form Text
1. Find endpoint: `POST /api/cv-creation/recommend-roles/`
2. Click "Try it out"
3. Enter this JSON:
   ```json
   {
     "text": "I have 5 years experience with Python, Django, and PostgreSQL"
   }
   ```
4. Click "Execute"
5. ✅ See the system automatically extract skills and recommend roles!

#### Option B: Test with Structured Input
1. Same endpoint: `POST /api/cv-creation/recommend-roles/`
2. Click "Try it out"
3. Enter this JSON:
   ```json
   {
     "skills": ["Python", "Django", "PostgreSQL"],
     "experience_years": 5
   }
   ```
4. Click "Execute"
5. ✅ See role recommendations!

---

## 📝 Free-Form Text Input (NEW Feature!)

Your system **automatically extracts** skills and experience from natural language!

### Example 1: Casual Input
```json
{
  "text": "Hey! I've been coding for 3 years, mainly Python and Django. I also know PostgreSQL and Docker."
}
```

**System extracts**:
- Skills: ["Python", "Django", "PostgreSQL", "Docker"]
- Experience: 3 years
- Returns: Role recommendations

### Example 2: Professional Input
```json
{
  "text": "Senior software engineer with 7 years of experience. Proficient in Python, Django, Flask, PostgreSQL, Redis, Docker, and Kubernetes."
}
```

**System extracts**:
- Skills: ["Python", "Django", "Flask", "PostgreSQL", "Redis", "Docker", "Kubernetes"]
- Experience: 7 years
- Returns: Senior Backend Developer (high confidence)

### Example 3: Beginner Input
```json
{
  "text": "I just graduated and learned JavaScript, React, and HTML/CSS. No work experience yet."
}
```

**System extracts**:
- Skills: ["JavaScript", "React", "HTML", "CSS"]
- Experience: 0 years
- Returns: Junior Frontend Developer

You'll see an interactive API documentation where you can test all endpoints!

---

## 📡 Available Endpoints

### 1. **POST** `/api/cv-creation/recommend-roles/`
Get career role recommendations

#### **Option A: Free-Form Text Input** (NEW!)
```json
{
  "text": "I'm a software developer with 5 years experience. I work with Python, Django, PostgreSQL, and Docker."
}
```

**Response**:
```json
{
  "success": true,
  "input_type": "free_text",
  "extracted_skills": ["Python", "Django", "Postgresql", "Docker"],
  "extracted_experience": 5.0,
  "confidence_metrics": {
    "skills_found": 4,
    "experience_detected": true,
    "text_length": 22,
    "extraction_quality": "good"
  },
  "recommendations": [
    {
      "role": "Backend Developer",
      "position": "Senior Backend Developer",
      "confidence": 0.87,
      "experience_level": "Senior",
      "matching_skills": ["Python", "Django", "Postgresql", "Docker"],
      "suggested_skills": ["Redis", "Kubernetes"],
      "description": "..."
    }
  ],
  "skill_insights": {...}
}
```

#### **Option B: Structured Input** (Original)
```json
{
  "skills": ["Python", "Django", "PostgreSQL", "Docker"],
  "experience_years": 5
}
```

**Response**:
```json
{
  "success": true,
  "input_type": "structured",
  "recommendations": [...],
  "skill_insights": {...}
}
```

---

### 2. **POST** `/api/cv-creation/extract-skills/`
Extract skills from free-form text (useful for testing extraction)

**Request**:
```json
{
  "text": "Full stack developer with expertise in React, Node.js, and MongoDB. 3 years of experience."
}
```

**Response**:
```json
{
  "success": true,
  "extracted_skills": ["React", "Node.js", "Mongodb"],
  "extracted_experience": 3.0,
  "confidence_metrics": {
    "skills_found": 3,
    "experience_detected": true,
    "text_length": 16,
    "extraction_quality": "good"
  },
  "original_text_preview": "Full stack developer with..."
}
```

---

### 3. **POST** `/api/cv-creation/skill-insights/`
Get detailed skill analysis

**Request**:
```json
{
  "skills": ["Python", "React", "Docker", "PostgreSQL"]
}
```

**Response**:
```json
{
  "success": true,
  "insights": {
    "total_skills": 4,
    "skill_categories": {
      "languages": ["Python"],
      "frontend": ["React"],
      "backend": ["Python"],
      "database": ["PostgreSQL"],
      "devops": ["Docker"]
    },
    "primary_focus": "backend",
    "is_full_stack": true,
    "has_data_skills": false,
    "has_devops_skills": true
  }
}
```

---

### 4. **GET** `/api/cv-creation/available-roles/`
List all 12 available roles

**Response**:
```json
{
  "success": true,
  "total_roles": 12,
  "roles": [
    {
      "role": "Backend Developer",
      "required_languages": ["Python", "Java", "C#", "Go", "Ruby", "PHP"],
      "common_technologies": ["Django", "Flask", "Spring", "PostgreSQL", "MySQL", "Redis"],
      "keywords": ["backend", "server", "api", "database", "microservices"]
    }
  ]
}
```

---

### 5. **GET** `/api/cv-creation/health/`
Check system health

**Response**:
```json
{
  "success": true,
  "status": "healthy",
  "recommender_loaded": true,
  "skill_extractor_loaded": true
}
```

---

## 🧪 Testing with cURL

### Free-Form Text Input
```bash
curl -X POST http://localhost:8000/api/cv-creation/recommend-roles/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I have 7 years of experience as a backend developer. Expert in Python, Django, PostgreSQL, Redis, and Docker. Also worked with Kubernetes and AWS."
  }'
```

### Extract Skills Only
```bash
curl -X POST http://localhost:8000/api/cv-creation/extract-skills/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mobile developer with 2 years experience in Swift, Kotlin, and React Native."
  }'
```

### Structured Input
```bash
curl -X POST http://localhost:8000/api/cv-creation/recommend-roles/ \
  -H "Content-Type: application/json" \
  -d '{
    "skills": ["Python", "Django", "PostgreSQL"],
    "experience_years": 3
  }'
```

---

## 🧪 Testing with PowerShell

### Free-Form Text
```powershell
$body = @{
    text = "I'm a data scientist with 4 years experience. I work with Python, TensorFlow, Pandas, and Jupyter."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/cv-creation/recommend-roles/" `
  -Method POST -Body $body -ContentType "application/json"
```

### Structured Input
```powershell
$body = @{
    skills = @("JavaScript", "React", "Node.js", "MongoDB")
    experience_years = 2
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/cv-creation/recommend-roles/" `
  -Method POST -Body $body -ContentType "application/json"
```

---

## 📝 Example Free-Form Texts to Try

### Resume-Style
```
I'm a Full Stack Developer with 5 years of professional experience.
I specialize in building web applications using Python, Django, and React.
Also have experience with PostgreSQL, Docker, and AWS.
Currently working on microservices architecture.
```

### LinkedIn Bio
```
Senior Data Scientist | 7+ years experience
Expert in Python, TensorFlow, PyTorch, and scikit-learn
Specialized in NLP and Computer Vision projects
Worked with Spark, Hadoop, and cloud platforms (AWS, GCP)
```

### Job Application
```
Hello, I'm applying for the backend developer position.
I have 3 years experience working with Node.js and Express.
I'm proficient in MongoDB and Redis for data management.
Also familiar with Docker and Kubernetes for deployment.
```

### Short Profile
```
Mobile developer with 2 years experience in Swift and Kotlin.
Built iOS and Android apps using React Native and Firebase.
```

### DevOps Profile
```
10 years of experience in DevOps and cloud infrastructure.
Expert in Kubernetes, Docker, Terraform, and Ansible.
Managed AWS and Azure cloud environments.
Strong experience with CI/CD using Jenkins and GitHub Actions.
```

### Fresh Graduate
```
Recent computer science graduate looking for junior developer role.
Built several projects using JavaScript, React, and Node.js.
Familiar with Git, MongoDB, and basic AWS services.
```

---

## 🎯 What the System Extracts

### Programming Languages
Python, JavaScript, TypeScript, Java, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, C++, Scala, R

### Frameworks
Django, Flask, FastAPI, React, Angular, Vue, Next.js, Node.js, Express, Spring, ASP.NET

### Databases
PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Cassandra, Oracle, SQL Server, DynamoDB

### DevOps & Cloud
Docker, Kubernetes, AWS, Azure, GCP, Terraform, Ansible, Jenkins, GitHub Actions, GitLab CI

### Data Science & ML
TensorFlow, PyTorch, scikit-learn, Pandas, NumPy, Keras, Spark, Hadoop, Kafka, Airflow

### Tools
Git, Linux, REST API, GraphQL, Microservices, Pytest, Jest, Selenium, Cypress, JUnit

### Experience Detection Patterns
- "5 years of experience"
- "10+ years experience"
- "worked for 3 years"
- "7 yrs experience"
- "experience: 2 years"

---

## 🔍 Understanding the Response

### Confidence Score (0.0 - 1.0)
- **1.00**: Perfect match (all requirements met)
- **0.80-0.99**: Strong match (most requirements met)
- **0.60-0.79**: Good match (core requirements met)
- **0.40-0.59**: Moderate match (some requirements met)
- **0.20-0.39**: Weak match (few requirements met)
- **< 0.20**: Poor match (minimal overlap)

### Experience Levels
- **Junior**: 0-2 years
- **Mid-Level**: 2-5 years
- **Senior**: 5-10 years
- **Lead**: 10+ years

### Extraction Quality
- **excellent**: 5+ skills found
- **good**: 3-4 skills found
- **fair**: 1-2 skills found
- **poor**: 0 skills found

---

## ⚠️ Important Notes

### What Works
✅ **Free-form text** (resumes, bios, descriptions)  
✅ **Structured JSON** (skill arrays + experience)  
✅ **Mixed case** (PYTHON, python, Python)  
✅ **Abbreviations** (js → JavaScript, py → Python, k8s → Kubernetes)  
✅ **Variants** (nodejs → Node.js, postgres → PostgreSQL)  
✅ **Experience detection** (multiple patterns)

### What Doesn't Work
❌ **Typos** (Pyton, Javasript) - Use correct spelling  
❌ **Soft skills** (leadership, communication) - Only technical skills  
❌ **Non-technical text** - Must mention specific technologies

### Tips for Best Results
1. **Mention specific technologies** (not just "programming")
2. **Include experience years** if you want accurate level assignment
3. **Use common technology names** (not proprietary tool names)
4. **Be specific** ("Python" is better than "coding")

---

## 🐛 Troubleshooting

### 403 Error: "Authentication credentials were not provided"
**Cause**: You're testing `/api/test/` which requires authentication  
**Solution**: Use the career recommendation endpoints instead - they don't require auth!

✅ **Working endpoints (no auth needed)**:
- `POST /api/cv-creation/recommend-roles/`
- `POST /api/cv-creation/skill-insights/`
- `GET /api/cv-creation/available-roles/`
- `GET /api/cv-creation/health/`

❌ **Don't use** (requires auth):
- `/api/test/`

### No Recommendations Returned
**Cause**: No technical skills detected in text  
**Solution**: Make sure to mention specific programming languages or frameworks

### Low Confidence Scores
**Cause**: Skills don't match role requirements well  
**Solution**: Your skills might fit multiple roles weakly - top result is still the best match

### Experience Not Detected
**Cause**: Experience not mentioned in recognizable format  
**Solution**: Use phrases like "5 years of experience" or "3+ years experience"

### Skills Not Extracted
**Cause**: Using non-standard names or typos  
**Solution**: Use standard technology names (see "What the System Extracts" above)

---

## 🎓 Example Swagger Workflow

1. **Start Server**: `python manage.py runserver`
2. **Open Swagger**: http://localhost:8000/swagger/
3. **Find Endpoint**: Click on `/api/cv-creation/recommend-roles/`
4. **Click "Try it out"**
5. **Enter Request Body**:
   ```json
   {
     "text": "Full stack developer with 4 years experience. Expert in Python, React, and PostgreSQL."
   }
   ```
6. **Click "Execute"**
7. **See Results**: Response shows extracted skills and recommendations!

---

## 📊 Testing Checklist

- [ ] Free-form text with skills and experience
- [ ] Free-form text with skills only (no experience)
- [ ] Free-form text with experience only (no skills)
- [ ] Structured input (original format)
- [ ] Empty text (should error)
- [ ] Non-technical text (should error)
- [ ] Multiple languages
- [ ] Abbreviations (js, ts, py)
- [ ] Various experience levels (0, 2, 5, 10+ years)
- [ ] Different role types (backend, frontend, data, devops, etc.)

---

**Ready to test?** Start the server and open http://localhost:8000/swagger/ 🚀
