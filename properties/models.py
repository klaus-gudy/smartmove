from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from clients.models import Client

class Property(models.Model):
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condominium'),
        ('townhouse', 'Townhouse'),
        ('office', 'Office'),
        ('warehouse', 'Warehouse'),
        ('other', 'Other'),
    ]
    
    property_id = models.CharField(max_length=20, unique=True)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='owned_properties')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='United States')
    
    # Property details
    bedrooms = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0)], null=True, blank=True)
    square_feet = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    floor_number = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    has_elevator = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_storage = models.BooleanField(default=False)
    
    # Access information
    access_instructions = models.TextField(blank=True, help_text="Special instructions for accessing the property")
    key_location = models.CharField(max_length=200, blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=17, blank=True)
    
    # Timestamps
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_created']
        verbose_name_plural = 'Properties'
        
    def __str__(self):
        return f"{self.property_id} - {self.address}, {self.city}"
    
    @property
    def full_address(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}, {self.country}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.property.property_id}"

class PropertyInventory(models.Model):
    ITEM_CONDITIONS = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inventory')
    room = models.CharField(max_length=100)
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=20, choices=ITEM_CONDITIONS, default='good')
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_fragile = models.BooleanField(default=False)
    requires_special_handling = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Property Inventories'
        
    def __str__(self):
        return f"{self.item_name} - {self.property.property_id}"
