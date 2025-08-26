from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from clients.models import Client
from properties.models import Property

class RelocationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    RELOCATION_TYPES = [
        ('local', 'Local Move'),
        ('long_distance', 'Long Distance Move'),
        ('international', 'International Move'),
        ('corporate', 'Corporate Relocation'),
    ]
    
    request_id = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='relocation_requests')
    origin_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='relocations_from')
    destination_property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='relocations_to', null=True, blank=True)
    
    # Destination address (if no property record exists)
    destination_address = models.TextField(blank=True)
    destination_city = models.CharField(max_length=100, blank=True)
    destination_state = models.CharField(max_length=100, blank=True)
    destination_zip = models.CharField(max_length=10, blank=True)
    destination_country = models.CharField(max_length=100, blank=True)
    
    relocation_type = models.CharField(max_length=20, choices=RELOCATION_TYPES, default='local')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Scheduling
    preferred_date = models.DateField()
    alternative_date = models.DateField(null=True, blank=True)
    scheduled_date = models.DateField(null=True, blank=True)
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_completion_date = models.DateTimeField(null=True, blank=True)
    
    # Services
    requires_packing = models.BooleanField(default=False)
    requires_unpacking = models.BooleanField(default=False)
    requires_storage = models.BooleanField(default=False)
    requires_insurance = models.BooleanField(default=True)
    requires_cleaning = models.BooleanField(default=False)
    
    # Cost estimation
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional information
    special_instructions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_relocations')
    
    # Timestamps
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_created']
        
    def __str__(self):
        return f"{self.request_id} - {self.client.full_name}"
    
    @property
    def full_destination_address(self):
        if self.destination_property:
            return self.destination_property.full_address
        return f"{self.destination_address}, {self.destination_city}, {self.destination_state} {self.destination_zip}, {self.destination_country}"
    
    @property
    def duration_days(self):
        if self.actual_start_date and self.actual_completion_date:
            return (self.actual_completion_date.date() - self.actual_start_date.date()).days
        return None

class RelocationQuote(models.Model):
    QUOTE_STATUS = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    relocation_request = models.ForeignKey(RelocationRequest, on_delete=models.CASCADE, related_name='quotes')
    quote_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=QUOTE_STATUS, default='draft')
    
    # Cost breakdown
    base_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    packing_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    transportation_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    storage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    additional_services_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Validity
    valid_until = models.DateField()
    terms_and_conditions = models.TextField()
    
    # Timestamps
    date_created = models.DateTimeField(auto_now_add=True)
    date_sent = models.DateTimeField(null=True, blank=True)
    date_responded = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Quote {self.quote_number} - {self.relocation_request.client.full_name}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost
        self.total_cost = (
            self.base_cost + self.packing_cost + self.transportation_cost + 
            self.insurance_cost + self.storage_cost + self.additional_services_cost + 
            self.tax_amount
        )
        super().save(*args, **kwargs)

class RelocationTimeline(models.Model):
    MILESTONE_TYPES = [
        ('quote_sent', 'Quote Sent'),
        ('quote_accepted', 'Quote Accepted'),
        ('survey_scheduled', 'Survey Scheduled'),
        ('survey_completed', 'Survey Completed'),
        ('packing_started', 'Packing Started'),
        ('packing_completed', 'Packing Completed'),
        ('loading_started', 'Loading Started'),
        ('loading_completed', 'Loading Completed'),
        ('in_transit', 'In Transit'),
        ('unloading_started', 'Unloading Started'),
        ('unloading_completed', 'Unloading Completed'),
        ('unpacking_started', 'Unpacking Started'),
        ('unpacking_completed', 'Unpacking Completed'),
        ('relocation_completed', 'Relocation Completed'),
    ]
    
    relocation_request = models.ForeignKey(RelocationRequest, on_delete=models.CASCADE, related_name='timeline')
    milestone_type = models.CharField(max_length=30, choices=MILESTONE_TYPES)
    description = models.CharField(max_length=200)
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    actual_datetime = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_datetime', 'date_created']
        
    def __str__(self):
        return f"{self.relocation_request.request_id} - {self.get_milestone_type_display()}"
