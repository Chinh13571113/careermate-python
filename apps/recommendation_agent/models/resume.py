from django.db import models
from .candidate import Candidate


# =====================================================
#  RESUME
# =====================================================
class Resume(models.Model):
    resume_id = models.AutoField(primary_key=True)
    about_me = models.TextField(null=True, blank=True)
    candidate = models.ForeignKey(
        Candidate,
        related_name='resumes',
        on_delete=models.CASCADE,
        db_column='candidate_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resume'

    def __str__(self):
        return f"Resume {self.resume_id} - {self.candidate.fullname}"
