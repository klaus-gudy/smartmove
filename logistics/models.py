from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import User
from relocations.models import RelocationRequest

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('van', 'Van'),
        ('truck_small', 'Small Truck'),
        ('truck_medium', 'Medium Truck'),
        ('truck_large', 'Large Truck'),
        ('trailer', 'Trailer'),
        ('container', 'Container'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('out_of_service', 'Out of Service'),
    ]
    
    vehicle_id = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(validators=[MinValueValidator(1990)])
    license_plate = models.CharField(max_length=15, unique=True)
    
    # Capacity
    max_weight_kg = models.IntegerField(validators=[MinValueValidator(1)])
    max_volume_cubic_meters = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0.1)])
    
    # Status and maintenance
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    last_service_date = models.DateField(null=True, blank=True)
    next_service_date = models.DateField(null=True, blank=True)
    mileage = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    
    # Insurance and documentation
    insurance_expiry = models.DateField()
    registration_expiry = models.DateField()
    
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.vehicle_id} - {self.make} {self.model} ({self.license_plate})"
    
    class Meta:
        ordering = ['vehicle_id']

class Driver(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_duty', 'On Duty'),
        ('off_duty', 'Off Duty'),
        ('on_leave', 'On Leave'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    driver_id = models.CharField(max_length=20, unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone = models.CharField(validators=[phone_regex], max_length=17)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17)
    
    # License information
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    cdl_class = models.CharField(max_length=10, blank=True, help_text="CDL class if applicable")
    
    # Employment
    hire_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Performance tracking
    total_moves = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.driver_id} - {self.user.get_full_name()}"
    
    class Meta:
        ordering = ['driver_id']

class MovingCrew(models.Model):
    crew_id = models.CharField(max_length=20, unique=True)
    crew_leader = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='led_crews')
    members = models.ManyToManyField(Driver, related_name='crew_memberships', blank=True)
    vehicles = models.ManyToManyField(Vehicle, related_name='assigned_crews', blank=True)
    max_capacity_kg = models.IntegerField(validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Crew {self.crew_id} - Leader: {self.crew_leader.user.get_full_name()}"
    
    class Meta:
        ordering = ['crew_id']

class MovingAssignment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    relocation_request = models.OneToOneField(RelocationRequest, on_delete=models.CASCADE, related_name='assignment')
    crew = models.ForeignKey(MovingCrew, on_delete=models.CASCADE, related_name='assignments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Scheduling
    scheduled_start_date = models.DateTimeField()
    scheduled_end_date = models.DateTimeField()
    actual_start_date = models.DateTimeField(null=True, blank=True)
    actual_end_date = models.DateTimeField(null=True, blank=True)
    
    # Route information
    estimated_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_distance_km = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Special requirements
    requires_special_equipment = models.BooleanField(default=False)
    special_equipment_notes = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Assignment {self.relocation_request.request_id} - Crew {self.crew.crew_id}"
    
    class Meta:
        ordering = ['-scheduled_start_date']

class InventoryTransfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('loaded', 'Loaded'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]
    
    assignment = models.ForeignKey(MovingAssignment, on_delete=models.CASCADE, related_name='inventory_transfers')
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_from = models.CharField(max_length=100)
    room_to = models.CharField(max_length=100, blank=True)
    
    # Physical properties
    estimated_weight_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in cm")
    is_fragile = models.BooleanField(default=False)
    requires_disassembly = models.BooleanField(default=False)
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    packed_datetime = models.DateTimeField(null=True, blank=True)
    loaded_datetime = models.DateTimeField(null=True, blank=True)
    delivered_datetime = models.DateTimeField(null=True, blank=True)
    
    # Condition tracking
    condition_notes = models.TextField(blank=True)
    damage_reported = models.BooleanField(default=False)
    damage_description = models.TextField(blank=True)
    
    handled_by = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.item_name} - {self.assignment.relocation_request.request_id}"
    
    class Meta:
        ordering = ['-date_created']

class MovingExpense(models.Model):
    EXPENSE_TYPES = [
        ('fuel', 'Fuel'),
        ('tolls', 'Tolls'),
        ('parking', 'Parking'),
        ('meals', 'Meals'),
        ('accommodation', 'Accommodation'),
        ('equipment_rental', 'Equipment Rental'),
        ('repairs', 'Vehicle Repairs'),
        ('other', 'Other'),
    ]
    
    assignment = models.ForeignKey(MovingAssignment, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.CharField(max_length=200)
    receipt_image = models.ImageField(upload_to='expense_receipts/', null=True, blank=True)
    date_incurred = models.DateField()
    submitted_by = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='submitted_expenses')
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_expense_type_display()} - ${self.amount} - {self.assignment}"
    
    class Meta:
        ordering = ['-date_incurred']
