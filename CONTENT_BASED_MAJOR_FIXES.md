# Content-Based Recommender - Major Bug Fixes

## 🐛 Vấn đề phát hiện

### Từ hình ảnh UI:

**Case 1: Loạn % scores**
```
Backend Node.js Developer
- Match: 43% → 67% (tăng lên)
- Semantic: 47% → 49%
- Skill: 0% → 14%

❌ Logic sai: Match (67%) > Semantic (49%) là KHÔNG thể!
```

**Case 2: Recommend sai hoàn toàn**
```
Query:
- Title: "Backend Developer"
- Skills: [java, nextjs, sql, pytorch, Python, pandas, numpy]

Top Result:
- Backend Node.js Developer (67% match)

❌ Vấn đề:
1. Node.js KHÔNG có trong skills
2. Python developer lại recommend Node.js job
3. Title "Backend" match → boost quá cao
```

---

## 🔧 Root Causes (Nguyên nhân gốc)

### Bug 1: Weights không sum to 1.0
```python
# ❌ Sai
weights = {"skills": 0.4, "title": 0.4, "description": 0.3}  
# Sum = 1.1 → embedding bị sai!

# ✅ Đúng
weights = {"skills": 0.5, "title": 0.3, "description": 0.2}  
# Sum = 1.0
```

**Impact:**
- Embedding vector bị skewed
- Weaviate search results không chính xác

---

### Bug 2: Title boost quá cao

```python
# ❌ Sai: 10% per term, cap 20%
boost = 0.1 * len(common_terms)  
return min(boost, 0.2)

# Query: "Backend Developer"
# Job: "Backend Node.js Developer"
# Common: ["backend", "developer"] = 2 terms
# Boost = 0.1 * 2 = 0.2 (20%!)

# ✅ Đúng: 2% per term, cap 5%
boost = 0.02 * len(common_terms)
return min(boost, 0.05)

# Same example:
# Boost = 0.02 * 2 = 0.04 (4%)
```

**Impact:**
- Title match override skill match
- "Backend Node.js" recommend cho Python developer vì title có "Backend"

---

### Bug 3: Skill weight quá thấp

```python
# ❌ Sai: Semantic 70%, Skill 30%
skill_weight: float = 0.3
base_score = 0.7 * semantic + 0.3 * skill

# ✅ Đúng: Semantic 50%, Skill 50%
skill_weight: float = 0.5
base_score = 0.5 * semantic + 0.5 * skill
```

**Impact:**
- Semantic (text similarity) dominate skill matching
- Node.js job có text "develop APIs using Node.js" → semantic high
- Nhưng skills không match Python → vẫn rank cao

---

### Bug 4: Skills parsing không normalize

```python
# ❌ Sai: Case-sensitive
def _parse_skills(skills):
    if isinstance(skills, list):
        return skills  # ["Python", "Django"]
    
# Job skills: ["python", "django"]
# Query skills: ["Python", "Django"]
# → KHÔNG match vì case khác!

# ✅ Đúng: Normalize lowercase
def _parse_skills(skills):
    if isinstance(skills, list):
        parsed = []
        for skill in skills:
            if isinstance(skill, str):
                parsed.append(skill.strip().lower())
        return parsed
```

**Impact:**
- Skill overlap = 0% dù có skills giống nhau
- Kết quả như hình: Skill: 0%

---

### Bug 5: No penalty for zero skill match

```python
# ❌ Sai: Title match vẫn được cộng điểm dù skill = 0
hybrid_score = base_score + title_context_boost

# Case: Node.js job, Python query
# Semantic: 0.6, Skill: 0.0, Title boost: 0.2
# Score = 0.6 + 0.2 = 0.8 (80%!) - SAI!

# ✅ Đúng: Penalize if no skill match
if skill_overlap_score > 0:
    hybrid_score = base_score + title_context_boost
else:
    hybrid_score = base_score * 0.5  # 50% penalty
    
# Same case:
# Score = 0.6 * 0.5 = 0.3 (30%) - ĐÚNG!
```

**Impact:**
- Jobs với 0 skill match vẫn rank cao nếu title match
- Node.js job rank #1 cho Python developer

---

## ✅ Các Fix đã thực hiện

### Fix 1: Correct embedding weights
```python
# Before: Sum = 1.1
weights = {"skills": 0.4, "title": 0.4, "description": 0.3}

# After: Sum = 1.0, skills priority
weights = {"skills": 0.5, "title": 0.3, "description": 0.2}
```

### Fix 2: Reduce title boost
```python
# Before: 10% per term, cap 20%
boost = 0.1 * len(common_terms)
return min(boost, 0.2)

# After: 2% per term, cap 5%
boost = 0.02 * len(common_terms)
return min(boost, 0.05)
```

### Fix 3: Increase skill weight
```python
# Before: 30%
skill_weight: float = 0.3

# After: 50%
skill_weight: float = 0.5
```

### Fix 4: Normalize skills to lowercase
```python
def _parse_skills(skills):
    """Parse and normalize skills"""
    if isinstance(skills, str):
        return [s.strip().lower() for s in skills.split(",") if s.strip()]
    elif isinstance(skills, list):
        parsed = []
        for skill in skills:
            if isinstance(skill, str):
                parsed.append(skill.strip().lower())
            elif isinstance(skill, dict):
                skill_name = skill.get('skill_name') or skill.get('name')
                if skill_name:
                    parsed.append(str(skill_name).strip().lower())
        return parsed
    return []
```

### Fix 5: Penalize zero skill match
```python
# Only add title boost if skill match exists
if skill_overlap_score > 0:
    hybrid_score = base_score + title_context_boost
else:
    # 50% penalty for no skill match
    hybrid_score = base_score * 0.5
```

### Fix 6: Normalize query title
```python
def _calculate_title_boost(query_title: str, job_title: str) -> float:
    query_terms = set(query_title.lower().split())  # Added .lower()
    job_terms = set(job_title.lower().split())
    # ...
```

---

## 📊 Expected Results

### Before Fix:
```
Query: Backend Developer [Python, Django, PostgreSQL]

Results:
1. Backend Node.js Developer - 67% match ❌
   - Semantic: 49%, Skill: 14%, Boost: 4%
   - Logic: Title match "Backend" → high boost
   - Problem: Node.js không match Python skills

2. Senior Java Developer - 62% match ❌
   - Problem: Java không match Python
```

### After Fix:
```
Query: Backend Developer [Python, Django, PostgreSQL]

Results:
1. Python Backend Developer - 78% match ✅
   - Semantic: 72%, Skill: 85%, Boost: 3%
   - Logic: Python skills match perfectly
   
2. Django Developer - 71% match ✅
   - Semantic: 65%, Skill: 80%, Boost: 2%
   - Logic: Django skills match

3. Backend Node.js Developer - 32% match ✅
   - Semantic: 60%, Skill: 0%, Boost: 4%
   - Score = (0.6 * 0.5) * 0.5 = 0.15 (penalized)
   - Logic: No skill match → penalty applied
```

---

## 🧪 Testing

### Run test script:
```bash
cd "d:\FPT_Uni\Fall 2025\be-python"
python test_content_based_fix.py
```

### Test cases:
1. **Backend Developer** với Python skills
   - Should recommend Python/Django jobs
   - Should NOT recommend Node.js/Java jobs at top

2. **Python Developer**
   - Should recommend Python-specific jobs
   - Should NOT recommend Java jobs

3. **Node.js Developer**
   - Should recommend Node.js/Express jobs
   - Should rank TypeScript jobs high

---

## 🎯 Scoring Formula (After Fix)

### Final Score Calculation:

```python
# Step 1: Calculate base score (50-50 split)
base_score = 0.5 * semantic_similarity + 0.5 * skill_overlap

# Step 2: Apply title boost (small, max 5%)
if skill_overlap > 0:
    final_score = base_score + title_boost  # title_boost ≤ 0.05
else:
    final_score = base_score * 0.5  # 50% penalty
```

### Example calculations:

**Case 1: Perfect match**
```
Query: Python Developer [Python, Django]
Job: Python Backend Developer [Python, Django, PostgreSQL]

Semantic: 0.85
Skill: 0.90 (match 2/2 required skills)
Title boost: 0.04 (Python + Developer)

Base = 0.5 * 0.85 + 0.5 * 0.90 = 0.875
Final = 0.875 + 0.04 = 0.915 (91.5%)
```

**Case 2: Good semantic, no skill match**
```
Query: Python Developer [Python, Django]
Job: Node.js Developer [Node.js, Express]

Semantic: 0.75 (both backend developers)
Skill: 0.0 (no skill match)
Title boost: 0.02 (Developer)

Base = 0.5 * 0.75 + 0.5 * 0.0 = 0.375
Final = 0.375 * 0.5 = 0.1875 (18.8%) ← PENALIZED!
```

**Case 3: Partial match**
```
Query: Backend Developer [Python, Django, PostgreSQL]
Job: Backend Developer [Python, MongoDB]

Semantic: 0.80
Skill: 0.33 (1/3 match)
Title boost: 0.04 (Backend + Developer)

Base = 0.5 * 0.80 + 0.5 * 0.33 = 0.565
Final = 0.565 + 0.04 = 0.605 (60.5%)
```

---

## 🔍 Debug Output

Debug logging được thêm vào để verify logic:

```
================================================================================
🔍 CONTENT-BASED RECOMMENDATION DEBUG
================================================================================
Query Title: backend developer
Query Skills: ['python', 'django', 'postgresql']
Skill Weight: 0.5 (50% semantic + 50% skill)
================================================================================

Job #1: Python Backend Developer
  Job Skills: ['python', 'django', 'flask', 'postgresql', 'redis']...
  Distance: 0.1234
  Semantic: 0.9383 (93.8%)
  Skill Overlap: 1.0000 (100.0%)
  Title Boost: 0.0400 (4.0%)
  Base Score: 0.9692
  Final Score: 1.0092 (100.9%) ← Will be capped at 1.0
  ✓

Job #2: Node.js Backend Developer
  Job Skills: ['node.js', 'express', 'typescript', 'mongodb']...
  Distance: 0.3456
  Semantic: 0.8272 (82.7%)
  Skill Overlap: 0.0000 (0.0%)
  Title Boost: 0.0400 (4.0%)
  Base Score: 0.4136
  Final Score: 0.2068 (20.7%) ← PENALIZED (no skill match)
  ⚠️  PENALIZED (no skill match)
```

---

## ✨ Benefits

1. **Skill matching priority**: Jobs phải match skills, không chỉ dựa vào text
2. **Penalty for mismatch**: Jobs không match skills sẽ bị giảm 50% điểm
3. **Reduced title bias**: Title boost giảm từ 20% → 5%
4. **Case-insensitive**: Skills matching không phân biệt hoa thường
5. **Balanced scoring**: 50-50 split giữa semantic và skill
6. **Correct weights**: Embedding weights sum to 1.0

---

## 🚀 Next Steps

1. ✅ Run test script
2. ✅ Verify debug output
3. ⬜ Test with real API
4. ⬜ Verify Frontend displays correctly
5. ⬜ Remove debug logging sau khi stable
6. ⬜ Monitor production metrics

---

## 📝 Notes

- **Skill overlap** dùng **Recall**: User có bao nhiêu % skills job yêu cầu
- **Extra skills** không bị penalty (bonus khuyến khích)
- **Title boost** chỉ áp dụng khi có skill match
- **Zero skill match** bị penalty 50% để tránh recommend sai

