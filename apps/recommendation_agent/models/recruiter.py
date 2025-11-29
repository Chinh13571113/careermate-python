from django.db import models
from .account import Account

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