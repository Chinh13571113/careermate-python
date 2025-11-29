from django.db import models
from .job_posting import JobPostings
from .candidate import Candidate


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