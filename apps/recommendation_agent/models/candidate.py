from django.db import models

from .account import Account


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