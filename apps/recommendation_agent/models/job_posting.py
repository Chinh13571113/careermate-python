from django.db import models
from .recruiter import Recruiter


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
        db_table = 'job_posting'
        managed = False
        ordering = ['-created_at']

    def __str__(self):
        return self.title
