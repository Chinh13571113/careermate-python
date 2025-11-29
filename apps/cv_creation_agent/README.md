# CV Creation Agent# Refined Career Recommendation System# CV Creation Agent - Career Recommendation System



Career recommendation engine that analyzes skills and experience to suggest best-fit roles.



## StructureA clean, simple, and effective career recommendation system that suggests roles and positions based on user's skills, technologies, and experience.A machine learning-powered career recommendation system that analyzes skills and experience to suggest **both career levels AND specific job roles** based on Stack Overflow survey data.



```

cv_creation_agent/

├── core/                          # Core business logic## 🎯 What It Does## 📋 Overview

│   ├── recommender.py            # Role recommendation engine

│   └── nlp_extractor.py          # NLP skill extraction

├── data/                          # Training data

│   ├── stackoverflow_cv_training_dataset.csv  # 65K+ records**Input**: User provides their skills (programming languages, frameworks, tools) and years of experienceThis system helps developers:

│   └── vocabulary/               # Skill mappings & aliases

├── tests/                         # Test files- 🎯 **Find Career Matches**: Match current skills to appropriate career levels (Junior/Mid/Senior/Principal)

│   ├── test_confidence.py        # Confidence testing

│   ├── test_edge_cases.py        # Edge case testing (30 tests)**Output**: System recommends matching career roles with confidence scores, showing:- 🏢 **Get Job Role Recommendations**: Discover specific roles like Backend, Frontend, Full-Stack, Data Professional, Mobile, DevOps

│   ├── test_free_text.py         # Free-text input testing

│   ├── test_system.py            # System integration tests- Best matching positions (e.g., "Mid-Level Backend Developer")- 📈 **Get Advancement Guidance**: Discover next steps in career progression  

│   ├── quick_test_free_text.py   # Quick demo script

│   └── quick_api_test.py         # Quick API test- Matching skills that qualify them- 🔍 **Identify Skill Gaps**: Learn what skills to develop for target positions/roles

├── docs/                          # Documentation

│   ├── DEVELOPMENT_GUIDE.md      # Development guide- Suggested skills to learn for improvement- 💰 **Salary Insights**: Get compensation data for similar profiles

│   ├── API_TESTING_GUIDE.md      # API testing guide

│   ├── TEST_RESULTS_COMPLETE.md  # Test results summary- Experience level assessment- 📚 **Learning Paths**: Receive prioritized skill development recommendations for specific roles

│   ├── FREE_TEXT_FEATURE_SUMMARY.md  # Free-text feature docs

│   ├── SWAGGER_QUICK_START.md    # Swagger guide- Skill profile insights- 🗺️ **Role Transition Planning**: Get detailed roadmaps for transitioning between roles

│   └── *.ipynb                   # Jupyter notebooks for analysis

├── views.py                       # API endpoints

├── urls.py                        # URL routing

├── serializers.py                 # DRF serializers## 📊 Data Source## ✨ New Job Role Features

├── swagger_schemas.py             # Swagger request schemas

├── models.py                      # Django models (empty)

└── apps.py                        # Django app config

```Based on **Stack Overflow Developer Survey** data containing real-world developer profiles, skills, and career paths.### 🎯 **Job Role Categories**



## Core Components- **Backend Developer**: Python, Docker, PostgreSQL, SQL, AWS, Kubernetes



### 1. Recommender Engine (`core/recommender.py`)Dataset: `data/stackoverflow_cv_training_dataset.csv` (65,437 developer records)- **Frontend Developer**: JavaScript, React, HTML/CSS, TypeScript, npm

- Pattern-based matching algorithm

- 12 career role definitions- **Full-Stack Developer**: JavaScript, React, Node.js, PostgreSQL, Docker  

- Confidence scoring (0-1)

- Experience level classification (Junior/Mid/Senior)## 🚀 Quick Start- **Data Professional**: Python, SQL, AWS, PostgreSQL, R, C++

- Skill gap analysis

- **Mobile Developer**: JavaScript, React Native, Swift, Kotlin, Java

### 2. NLP Extractor (`core/nlp_extractor.py`)

- Extract skills from free-form text### 1. Start the Server- **DevOps Engineer**: Docker, Kubernetes, AWS, Bash, Python, Terraform

- Extract years of experience from text

- Skill vocabulary matching (aliases, variations)

- Text preprocessing and normalization

```bash### 📊 **Smart Role Matching**

### 3. API Views (`views.py`)

- `recommend_roles()` - Main recommendation endpointcd "d:\SEP490\BE PY\be-python"- Skill coverage percentages for each role

- `extract_skills_from_text()` - Skill extraction endpoint

- `get_skill_insights()` - Skill analysis endpointpython manage.py runserver- Confidence levels (High/Medium/Low) based on skill alignment

- `get_available_roles()` - List all roles

- `health_check()` - Health status```- Role-specific skill gap analysis



## Available Career Roles- Experience-weighted recommendations



1. **Backend Developer** - Server-side developmentYou should see:

2. **Frontend Developer** - Client-side development

3. **Full Stack Developer** - Both frontend & backend```## 🏗️ Architecture

4. **Mobile Developer** - iOS/Android development

5. **DevOps Engineer** - Infrastructure & CI/CD✅ Career Recommender initialized

6. **Data Scientist** - ML & analytics

7. **Data Engineer** - Data pipelines``````

8. **Machine Learning Engineer** - ML systems

9. **Cloud Engineer** - Cloud infrastructurecv_creation_agent/

10. **Security Engineer** - Security & compliance

11. **QA Engineer** - Testing & quality### 2. Test the System├── 📓 stackoverflow_survey_exploration.ipynb   # Data exploration notebook

12. **UI/UX Engineer** - Design & user experience

├── 🗂️ data/

## Performance Metrics

```bash│   ├── stackoverflow_cv_training_dataset.csv   # Training dataset (65k profiles)

- **Accuracy**: 90% (9/10 test scenarios passed)

- **Edge Cases**: 93.3% (28/30 passed)python apps/cv_creation_agent/test_system.py│   ├── cv_dataset_summary.txt                  # Dataset documentation

- **Response Time**: < 100ms average

- **Dataset Size**: 65,437 training records```│   └── cv_columns_mapping.txt                  # Column descriptions



## Testing├── 🤖 ml/



Run all tests:### 3. Make API Calls│   ├── career_recommender.py                   # Core ML model

```bash

# From cv_creation_agent directory│   └── __init__.py

python tests/test_confidence.py

python tests/test_edge_cases.py```bash├── ⚙️ services/

python tests/test_free_text.py

python tests/test_system.py# Recommend roles│   ├── career_service.py                       # Business logic layer

```

curl -X POST http://localhost:8000/api/cv-creation/recommend-roles/ \│   └── __init__.py

Quick tests:

```bash  -H "Content-Type: application/json" \├── 🌐 views.py                                 # Django REST API endpoints

python tests/quick_test_free_text.py

python tests/quick_api_test.py  -d '{"skills": ["Python", "Django", "PostgreSQL"], "experience_years": 3}'├── 🔗 urls.py                                  # URL routing

```

├── 🚀 train_model.py                           # Model training script

## Documentation

# Get skill insights├── 🧪 test_career_system.py                    # Demo and testing

All documentation is in the `docs/` folder:

- **DEVELOPMENT_GUIDE.md** - How to develop and extend the systemcurl -X POST http://localhost:8000/api/cv-creation/skill-insights/ \├── ⚡ setup_career_system.py                   # Setup automation

- **API_TESTING_GUIDE.md** - How to test the API

- **TEST_RESULTS_COMPLETE.md** - Complete test results  -H "Content-Type: application/json" \└── 📦 requirements_cv_agent.txt                # Dependencies

- **FREE_TEXT_FEATURE_SUMMARY.md** - Free-text input feature guide

  -d '{"skills": ["Python", "React", "Docker"]}'```

## Data



Training data is in `data/` folder:

- `stackoverflow_cv_training_dataset.csv` - Main dataset (65K+ records)# Get available roles## 🚀 Quick Start

- `vocabulary/skills_vocabulary.json` - Master skill list

- `vocabulary/skills_aliases.json` - Skill name variationscurl http://localhost:8000/api/cv-creation/available-roles/



## API Usage### 1. Generate Training Data



### Recommend Roles (Free Text)# Health check```bash

```python

POST /api/cv-creation/recommend-roles/curl http://localhost:8000/api/cv-creation/health/# Open and run the Jupyter notebook

{

  "text": "I have 5 years experience with Python, Django, and React"```jupyter notebook stackoverflow_survey_exploration.ipynb

}

```# Run all cells to generate: data/stackoverflow_cv_training_dataset.csv



### Recommend Roles (Structured)## 📡 API Endpoints```

```python

POST /api/cv-creation/recommend-roles/

{

  "skills": ["Python", "Django", "React"],### POST `/api/cv-creation/recommend-roles/`### 2. Setup System

  "experience_years": 5

}```bash

```

Recommend career roles based on skills and experience.# Install dependencies

### Extract Skills

```pythonpip install scikit-learn pandas numpy

POST /api/cv-creation/extract-skills/

{**Request:**

  "text": "Backend developer with 3 years. Java, Spring Boot."

}```json# Run automated setup

```

{python setup_career_system.py

### Get Skill Insights

```python  "skills": ["Python", "Django", "PostgreSQL", "Docker"],```

POST /api/cv-creation/skill-insights/

{  "experience_years": 3

  "skills": ["Python", "React", "Docker"]

}}### 3. Test the System

```

``````bash

## Technology

# Run demo examples

- **Algorithm**: Pattern matching (no ML/embeddings)

- **NLP**: Custom skill extraction**Response:**python test_career_system.py

- **Data**: Stack Overflow survey dataset

- **Performance**: Pure Python, < 100ms response time```json```



## Extension Points{



To add new roles, edit `core/recommender.py`:  "success": true,## 📊 Dataset

```python

ROLE_PATTERNS = {  "recommendations": [

    "Your New Role": {

        "required_languages": ["Language1", "Language2"],    {**Source**: Stack Overflow Annual Developer Survey  

        "common_technologies": ["Tech1", "Tech2"],

        "keywords": ["keyword1", "keyword2"],      "role": "Backend Developer",**Profiles**: 65,437 developer profiles  

        "description": "Role description"

    }      "position": "Mid-Level Backend Developer",**Features**: 36 optimized columns (reduced from 114)  

}

```      "confidence": 0.87,**Size**: ~59MB focused dataset  



To add new skills, edit `data/vocabulary/skills_vocabulary.json`.      "experience_level": "Mid-Level",


      "matching_skills": ["Python", "Django", "PostgreSQL", "Docker"],### Key Features

      "suggested_skills": ["Redis", "Kubernetes", "REST API"],- **Demographics**: Age, experience, education level

      "description": "Mid-Level backend developer focusing on server-side logic, databases, and APIs"- **Technical Skills**: 180+ programming languages, frameworks, tools

    }- **Experience**: Years coding, years professional, developer type

  ],- **Compensation**: Salary data with currency normalization

  "total_skills": 4,- **Work Context**: Company size, remote work, industry

  "skill_insights": {

    "total_skills": 4,## 🤖 Machine Learning Model

    "primary_focus": "backend",

    "is_full_stack": false,### CareerPathRecommender Class

    "has_data_skills": false,

    "has_devops_skills": true**Algorithm**: TF-IDF + Cosine Similarity + K-Means Clustering

  }**Career Levels**: Junior → Mid-Level → Senior → Principal

}**Skills Database**: 180+ unique technical skills

```

#### Key Methods

### POST `/api/cv-creation/skill-insights/````python

# Train the model

Get insights about a skill profile.recommender.train('data/stackoverflow_cv_training_dataset.csv')



**Request:**# Match skills to career level

```jsonresult = recommender.match_skills_to_career(['Python', 'Django'], 3)

{

  "skills": ["Python", "React", "Docker", "PostgreSQL"]# Get skill gap analysis

}gaps = recommender.get_skill_recommendations(['Python'], 'Senior Developer')

```

# Find similar developers

**Response:**similar = recommender.find_similar_developers(['React', 'JavaScript'], 2)

```json```

{

  "success": true,## 🌐 API Endpoints

  "insights": {

    "total_skills": 4,### Job Role Recommendations (NEW!)

    "skill_categories": {```http

      "languages": ["Python"],POST /cv-agent/career/recommend-job-roles/

      "frontend": ["React"],Content-Type: application/json

      "backend": ["Python"],

      "database": ["PostgreSQL"],{

      "devops": ["Docker"]    "skills": ["Python", "Django", "PostgreSQL"],

    },    "experience_years": 3

    "primary_focus": "backend",}

    "is_full_stack": true,

    "has_data_skills": false,Response:

    "has_devops_skills": true{

  }    "recommended_roles": [

}        {

```            "role": "Backend Developer",

            "match_score": 0.72,

### GET `/api/cv-creation/available-roles/`            "skill_coverage": 60.0,

            "matching_skills": ["Python", "PostgreSQL", "Django"],

Get list of all available roles that can be recommended.            "missing_skills": ["Docker", "Kubernetes", "Redis"],

            "confidence": "High"

**Response:**        }

```json    ]

{}

  "success": true,```

  "total_roles": 12,

  "roles": [### Role Learning Path (NEW!)

    {```http

      "role": "Backend Developer",POST /cv-agent/career/role-learning-path/

      "required_languages": ["Python", "Java", "C#", "Go", "Ruby"],Content-Type: application/json

      "common_technologies": ["Django", "Flask", "Spring", "Node.js", "PostgreSQL"],

      "keywords": ["backend", "server", "api", "database", "microservices"]{

    }    "current_skills": ["HTML", "CSS", "JavaScript"],

  ]    "target_role": "Frontend Developer"

}}

```

Response:

### GET `/api/cv-creation/health/`{

    "target_role": "Frontend Developer",

Health check endpoint.    "current_coverage": 30.0,

    "missing_skills_count": 7,

**Response:**    "total_estimated_hours": 280,

```json    "learning_plan": [

{        {

  "success": true,            "skill": "React",

  "status": "healthy",            "priority": 8,

  "recommender_loaded": true            "estimated_hours": 40,

}            "difficulty": "Intermediate"

```        }

    ]

## 🎨 Supported Roles}

```

The system can recommend these 12 career roles:

### Available Job Roles (NEW!)

1. **Backend Developer** - Server-side logic, databases, APIs```http

2. **Frontend Developer** - UI/UX, web interfaces, responsive designGET /cv-agent/career/available-job-roles/

3. **Full Stack Developer** - Both frontend and backend

4. **Data Scientist** - Data analysis, machine learning, statisticsResponse:

5. **Data Engineer** - Data pipelines, ETL, big data infrastructure{

6. **DevOps Engineer** - CI/CD, infrastructure, automation    "job_roles": [

7. **Mobile Developer** - iOS and Android applications        "Backend Developer", 

8. **Machine Learning Engineer** - ML model deployment and optimization        "Frontend Developer", 

9. **Cloud Engineer** - Cloud infrastructure and scalability        "Full-Stack Developer",

10. **QA Engineer** - Software testing and quality assurance        "Data Professional",

11. **Security Engineer** - Cybersecurity and system protection        "Mobile Developer",

12. **Database Administrator** - Database management and optimization        "DevOps Engineer"

    ],

## 📁 Project Structure    "count": 6

}

``````

cv_creation_agent/

├── data/                              # Stack Overflow survey data### Career Level Recommendations (Existing)

│   ├── stackoverflow_cv_training_dataset.csv```http

│   └── vocabulary/POST /cv-agent/career/recommend/

├── recommender.py                     # Core recommendation engineContent-Type: application/json

├── views.py                           # Django REST API endpoints

├── urls.py                            # URL routing{

├── models.py                          # Database models (placeholder)    "skills": ["Python", "Django", "PostgreSQL"],

├── serializers.py                     # DRF serializers (placeholder)    "experience_years": 3

├── test_system.py                     # System tests}

├── stackoverflow_dataset_analysis.ipynb    # Data exploration```

└── stackoverflow_survey_exploration.ipynb  # Survey analysis

```### Skill Gap Analysis

```http

## 🧠 How It WorksPOST /cv-agent/career/skill-gaps/

Content-Type: application/json

### 1. Skill Normalization

User skills are normalized to handle variations:{

- "js" → "javascript"    "current_skills": ["Python", "Django"],

- "nodejs" → "node.js"    "target_position": "Senior Developer"

- "py" → "python"}

- etc.```



### 2. Role Matching### Skill Validation

For each role, the system:```http

- Compares user skills against role requirements (languages + technologies)POST /cv-agent/career/validate-skills/

- Calculates match score (0.0 to 1.0)Content-Type: application/json

- Weights programming languages higher than frameworks/tools

{

### 3. Experience Assessment    "skills": ["Python", "React", "Unknown-Skill"]

- **Junior**: 0-2 years}

- **Mid-Level**: 2-5 years```

- **Senior**: 5-10 years

- **Lead**: 10+ years### Learning Path Recommendations

```http

### 4. Confidence ScoringPOST /cv-agent/career/learning-path/

Confidence score formula:Content-Type: application/json

```python

score = (language_matches * 1.5 + tech_matches) / (total_requirements) * 2{

score = min(score, 1.0)  # Cap at 1.0    "current_skills": ["HTML", "CSS"],

```    "target_skills": ["React", "Node.js", "MongoDB"]

}

### 5. Recommendations```

Returns top 5 roles sorted by confidence, including:

- Matching skills (what qualifies them)### Available Skills List

- Suggested skills (what to learn next)```http

- Experience-appropriate position titleGET /cv-agent/career/skills/

```

## 🔧 Technology Stack

### Industry Insights

- **Django 5.2.7** - Web framework```http

- **Python 3.12** - Programming languagePOST /cv-agent/career/insights/

- **pandas** - Data analysis (for dataset)Content-Type: application/json

- **No external dependencies** for core recommendation (pure Python)

- **No database required** - Stateless recommendation engine{

- **No Docker required** - Simple deployment    "skills": ["AWS", "Docker", "Kubernetes"],

    "experience_years": 5

## 🧪 Testing}

```

### Run All Tests

```bash## 💼 Business Logic Layer

python apps/cv_creation_agent/test_system.py

```### CareerRecommendationService



### Test Specific Scenarios**Features**:

- Enhanced skill validation with fuzzy matching

**Backend Developer (3 years):**- Learning time estimation (40-120 hours per skill)

```json- Priority-based skill ranking

{"skills": ["Python", "Django", "PostgreSQL", "Docker"], "experience_years": 3}- Industry salary insights

```- Technology trend analysis



**Frontend Developer (2 years):**## 📈 Example Usage

```json

{"skills": ["JavaScript", "React", "TypeScript", "HTML", "CSS"], "experience_years": 2}### Job Role Recommendations (NEW!)

``````python

from ml.career_recommender import CareerPathRecommender

**Full-stack Developer (5 years):**

```jsonrecommender = CareerPathRecommender()

{"skills": ["JavaScript", "React", "Node.js", "Python", "PostgreSQL"], "experience_years": 5}recommender.load_model('ml/career_recommender_model.pkl')

```

# Get job role recommendations

**Data Scientist (4 years):**role_recs = recommender.recommend_job_roles(

```json    ['JavaScript', 'React', 'HTML/CSS', 'TypeScript'], 

{"skills": ["Python", "pandas", "scikit-learn", "TensorFlow", "SQL"], "experience_years": 4}    experience_years=3

```)



**DevOps Engineer (6 years):**print("Top recommended role:", role_recs['recommended_roles'][0]['role'])

```jsonprint("Skill coverage:", role_recs['recommended_roles'][0]['skill_coverage'])

{"skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Python"], "experience_years": 6}print("Skills to learn:", role_recs['recommended_roles'][0]['missing_skills'])

```

# Output:

## 📈 Data Analysis# Top recommended role: Frontend Developer

# Skill coverage: 50.0%

Explore the Stack Overflow dataset with Jupyter notebooks:# Skills to learn: ['Angular', 'Vue.js', 'Firebase']

```

```bash

jupyter notebook apps/cv_creation_agent/stackoverflow_dataset_analysis.ipynb### Role Learning Path (NEW!)

``````python

# Get learning path for specific role

The notebooks provide insights on:learning_path = recommender.get_role_learning_path(

- Developer demographics    current_skills=['Python', 'SQL'],

- Skill distributions    target_role='Data Professional'

- Salary ranges by role)

- Experience levels

- Technology trendsprint(f"Current coverage: {learning_path['current_coverage']:.1f}%")

print(f"Total learning time: {learning_path['total_estimated_hours']} hours")

## 🎯 Design Principlesprint("Priority skills:", [item['skill'] for item in learning_path['learning_plan'][:3]])



1. **Simple**: No complex ML models, no vector databases, no Docker dependencies# Output:

2. **Fast**: Pure Python, in-memory matching, sub-second responses# Current coverage: 20.0%

3. **Accurate**: Based on real-world data from 65K+ developers# Total learning time: 240 hours

4. **Maintainable**: Clean code, clear logic, easy to understand# Priority skills: ['Docker', 'AWS', 'PostgreSQL']

5. **Extensible**: Easy to add new roles or modify matching logic```



## 🔄 Future Enhancements### Basic Career Level Matching (Existing)

```python

Possible improvements (not implemented yet):# Basic career matching

- [ ] Add salary predictionsresult = recommender.match_skills_to_career(

- [ ] Include location-based recommendations    ['JavaScript', 'React', 'HTML/CSS'], 

- [ ] Add company size preferences    experience_years=1

- [ ] Remote work indicators)

- [ ] Career path suggestions (next steps)

- [ ] Skill gap analysis with learning resourcesprint(f"Career Level: {result['current_level']}")

print(f"Skill Match: {result['skill_match_score']:.2f}")

## 📝 Notesprint(f"Average Salary: ${result['avg_salary_similar']:,.0f}")

```

- **No database models yet**: Currently stateless, doesn't store user data

- **No authentication**: Open API for testing### Skill Gap Analysis

- **No rate limiting**: For development only```python

- **CSRF disabled**: For easy testing (re-enable in production)# What skills do I need for Senior Developer?

gaps = recommender.get_skill_recommendations(

## ✅ What Was Cleaned Up    current_skills=['Python', 'Django'],

    target_position='Senior Developer'

Removed all unnecessary complexity:)

- ❌ Weaviate vector database

- ❌ Docker compose filesprint(f"Skills to learn: {gaps['skills_to_learn']}")

- ❌ Complex ML model trainingprint(f"Current coverage: {gaps['skill_coverage']:.1%}")

- ❌ Pattern-based role extraction```

- ❌ Multiple service layers

- ❌ Redundant parsers and utilities## 🔧 Configuration

- ❌ 20+ markdown documentation files

- ❌ Multiple test scripts### Model Parameters

- **TF-IDF**: Captures skill importance and rarity

Kept only essentials:- **Similarity Threshold**: 0.3 (adjustable for matching strictness)

- ✅ Core recommendation engine (`recommender.py`)- **Clustering**: K-means for developer grouping

- ✅ Clean API views (`views.py`)- **Career Levels**: Experience-based progression (0-2, 3-5, 6-10, 11+ years)

- ✅ Simple routing (`urls.py`)

- ✅ Stack Overflow dataset### Skill Categories

- ✅ Jupyter notebooks for analysis- **Programming Languages**: Python, JavaScript, Java, etc.

- ✅ One comprehensive test script- **Frameworks**: React, Django, Angular, etc.  

- **Databases**: PostgreSQL, MongoDB, Redis, etc.

## 🚀 Ready to Use- **DevOps**: Docker, Kubernetes, AWS, etc.

- **Tools**: Git, Linux, VS Code, etc.

The system is **fully functional** and ready to use right now:

## 🧪 Testing

```bash

# 1. Start serverRun comprehensive tests:

python manage.py runserver```bash

# Test enhanced system with job role recommendations

# 2. Test itpython test_enhanced_career_system.py

python apps/cv_creation_agent/test_system.py

# Test basic functionality  

# 3. Use itpython test_career_system.py

curl -X POST http://localhost:8000/api/cv-creation/recommend-roles/ \```

  -H "Content-Type: application/json" \

  -d '{"skills": ["Python", "Django"], "experience_years": 3}'**Enhanced Test Cases Include:**

```- ✅ **Job Role Matching**: Backend, Frontend, Full-Stack, Data Professional

- ✅ **Skill Coverage Analysis**: Percentage match for each role

**That's it!** Simple, clean, and effective. 🎉- ✅ **Learning Path Generation**: Prioritized skill recommendations  

- ✅ **Role Transition Planning**: Roadmaps between different roles
- ✅ **Confidence Scoring**: High/Medium/Low confidence levels

**Test Scenarios:**
- Aspiring Backend Developer (Python, Django, PostgreSQL, Docker)
- Frontend Developer Candidate (JavaScript, React, HTML/CSS, TypeScript)  
- Full-Stack Generalist (JavaScript, React, Node.js, PostgreSQL, Docker)
- Data Science Professional (Python, SQL, AWS, Docker, PostgreSQL)

## 📁 File Descriptions

| File | Purpose |
|------|---------|
| `career_recommender.py` | Core ML model with TF-IDF and clustering |
| `career_service.py` | Business logic with enhanced features |
| `views.py` | Django REST API endpoints |
| `train_model.py` | Model training and initialization |
| `test_career_system.py` | Demo examples and validation |
| `setup_career_system.py` | Automated setup and validation |

## 🎯 Next Steps

1. **Run the notebook** to generate training data
2. **Execute setup script** to initialize the model  
3. **Test the system** with demo examples
4. **Integrate with Django** for web API access
5. **Customize** skill categories for your use case

## 🔍 Troubleshooting

**Model not found**: Run setup script to train model  
**Import errors**: Check Python path and dependencies  
**Dataset missing**: Run Jupyter notebook to generate data  
**Low accuracy**: Retrain with more recent survey data

---

*Built with scikit-learn, Django, and Stack Overflow survey data*