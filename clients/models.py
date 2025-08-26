from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Client(models.Model):
    INDIVIDUAL = 'individual'
    CORPORATE = 'corporate'
    CLIENT_TYPES = [
        (INDIVIDUAL, 'Individual'),
        (CORPORATE, 'Corporate'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    client_id = models.CharField(max_length=20, unique=True)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES, default=INDIVIDUAL)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='United States')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_created']
        
    def __str__(self):
        if self.client_type == self.CORPORATE and self.company_name:
            return f"{self.company_name} ({self.client_id})"
        return f"{self.first_name} {self.last_name} ({self.client_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}, {self.country}"

class ClientDocument(models.Model):
    DOCUMENT_TYPES = [
        ('id', 'ID Document'),
        ('passport', 'Passport'),
        ('lease', 'Lease Agreement'),
        ('insurance', 'Insurance Document'),
        ('other', 'Other'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_name = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='client_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client.full_name} - {self.document_name}"
