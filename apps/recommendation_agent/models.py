from django.db import models


# =====================================================
#  ACCOUNT & RECRUITER
# =====================================================

class Account(models.Model):
    account_id = models.AutoField(primary_key=True, db_column='id')
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, db_column='username', blank=True, null=True)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=50, blank=True, null=True, default='ACTIVE')

    class Meta:
        db_table = 'account'
        managed = False

    def __str__(self):
        return self.full_name or self.email


class Recruiter(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING, db_column='account_id')
    company_name = models.CharField(max_length=255)
    website = models.CharField(max_length=255, blank=True, null=True)
    logo_url = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'recruiters'
        managed = False

    def __str__(self):
        return self.company_name


# =====================================================
#  CANDIDATE
# =====================================================

class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True, db_column='candidate_id')
    dob = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    job_level = models.CharField(max_length=100, blank=True, null=True)
    exp_year = models.IntegerField(blank=True, null=True, db_column='experience')
    fullname = models.CharField(max_length=255, db_column='full_name', blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING, db_column='account_id')

    class Meta:
        db_table = 'candidate'
        managed = False

    def __str__(self):
        return self.fullname or f"Candidate {self.candidate_id}"


# =====================================================
#  JOB POSTING & DESCRIPTION & SKILL
# =====================================================

class JobPostings(models.Model):
    id = models.AutoField(primary_key=True)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.DO_NOTHING, db_column='recruiter_id')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    expiration_date = models.DateField(db_column='expiration_date', blank=True, null=True)
    created_at = models.DateField(db_column='create_at', blank=True, null=True)

    class Meta:
        db_table = 'job_postings'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class JDSkill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'jd_skills'
        managed = False

    def __str__(self):
        return self.name


class JobDescription(models.Model):
    id = models.AutoField(primary_key=True)
    jd_skill = models.ForeignKey(JDSkill, on_delete=models.DO_NOTHING, db_column='skill_id')
    job_posting = models.ForeignKey(JobPostings, on_delete=models.DO_NOTHING, db_column='job_posting_id')
    must_have = models.BooleanField(default=False, db_column='must_to_have')
    experience_year = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'job_descriptions'
        managed = False

    def __str__(self):
        return f"{self.job_posting.title} - {self.jd_skill.name}"


# =====================================================
#  JOB APPLY
# =====================================================

class JobApply(models.Model):
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey(JobPostings, on_delete=models.DO_NOTHING, db_column='job_id')
    candidate = models.ForeignKey(Candidate, on_delete=models.DO_NOTHING, db_column='candidate_id')
    status = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(db_column='create_at', blank=True, null=True)

    class Meta:
        db_table = 'job_apply'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.candidate.fullname} → {self.job.title}"


# =====================================================
#  JOB FEEDBACK
# =====================================================

class JobFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('save', 'Save'),
        ('apply', 'Apply'),
    ]

    id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, db_column='candidate_id', related_name='feedbacks')
    job = models.ForeignKey(JobPostings, on_delete=models.CASCADE, db_column='job_id', related_name='feedbacks')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    score = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True, db_column='create_at')

    class Meta:
        db_table = 'job_feedback'
        unique_together = ('candidate', 'job', 'feedback_type')
        indexes = [
            models.Index(fields=['candidate']),
            models.Index(fields=['job']),
            models.Index(fields=['feedback_type']),
        ]

    def __str__(self):
        return f"{self.candidate.fullname} - {self.job.title} - {self.feedback_type}"

