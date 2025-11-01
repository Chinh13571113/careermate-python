from django.db import models
from .candidate import Candidate
from .job_posting import JobPostings


# =====================================================
#  JOB FEEDBACK
# =====================================================

class JobFeedback(models.Model):
    class FeedbackType(models.TextChoices):
        APPLY = 'apply', 'Apply'
        LIKE = 'like', 'Like'
    job_feedback_id = models.AutoField(primary_key=True)
    #feedback_type_choices = [
    #    ('dislike', 'Dislike'),
    #    ('like', 'Like'),
    #    ('apply', 'Apply'),]

    feedback_type = models.CharField(max_length=10, choices=FeedbackType.choices, default=FeedbackType.APPLY)
    score = models.FloatField(null=True, blank=True)
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='job_feedbacks',   # 1 candidate có nhiều feedback
        db_column='candidate_id'
    )

    job = models.ForeignKey(
        JobPostings,
        on_delete=models.CASCADE,
        related_name='feedbacks',# 1 job có nhiều feedback
        db_column='job_id'
    )

    class Meta:
        db_table = 'job_feedback'
        unique_together = ('candidate', 'job', 'feedback_type')
        indexes = [
            models.Index(fields=['candidate']),
            models.Index(fields=['job']),
            models.Index(fields=['feedback_type']),
        ]

    def __str__(self):
        return f"Feedback #{self.job_feedback_id} - {self.candidate.fullname} → {self.job.title}"
