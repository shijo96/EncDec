from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Testator(models.Model):
    USER = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    id_proof = models.FileField(upload_to='testator_id/', null=True, blank=True)
    death_certificate = models.FileField(upload_to='death_certificate/', null=True, blank=True)
    deceased_date = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('deceased', 'Deceased')], default='active')
    approval_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')




class Will_document(models.Model):
    USER = models.OneToOneField(User, on_delete=models.CASCADE)
    TESTATOR = models.ForeignKey(Testator, on_delete=models.CASCADE)
    file = models.FileField(upload_to='will_document/', null=True, blank=True)
    description = models.CharField(max_length=255)
    encryption_key = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=255)
    date = models.CharField(max_length=255)


class Beneficiary(models.Model):
    WILL_DOCUMENT = models.ForeignKey(Will_document, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    

class Notification(models.Model):
    WILL_DOCUMENT = models.ForeignKey(Will_document, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
  



class Upload(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='hash_checking/', null=True, blank=True)
    result = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
  