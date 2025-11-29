from django.db import models
from .resume import Resume


# =====================================================
#  SKILL
# =====================================================
class Skill(models.Model):
    skill_id = models.AutoField(primary_key=True)
    skill_type = models.CharField(max_length=100, null=True, blank=True)
    skill_name = models.CharField(max_length=100)
    year_of_experience = models.IntegerField(null=True, blank=True)
    resume = models.ForeignKey(
        Resume,
        related_name='skills',
        on_delete=models.CASCADE,
        db_column="resume_id"
    )

    class Meta:
        db_table = 'skill'

    def __str__(self):
        return f"{self.skill_name} ({self.year_of_experience} yrs)"