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