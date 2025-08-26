from django.contrib import admin
from .models import Vehicle, Driver, MovingCrew, MovingAssignment, InventoryTransfer, MovingExpense

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_id', 'vehicle_type', 'make', 'model', 'year', 'license_plate', 'status', 'max_weight_kg']
    list_filter = ['vehicle_type', 'status', 'make', 'year']
    search_fields = ['vehicle_id', 'license_plate', 'make', 'model']
    readonly_fields = ['date_created']
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('vehicle_id', 'vehicle_type', 'make', 'model', 'year', 'license_plate')
        }),
        ('Capacity', {
            'fields': ('max_weight_kg', 'max_volume_cubic_meters')
        }),
        ('Status & Maintenance', {
            'fields': ('status', 'mileage', 'last_service_date', 'next_service_date')
        }),
        ('Documentation', {
            'fields': ('insurance_expiry', 'registration_expiry')
        }),
        ('System', {
            'fields': ('is_active', 'date_created')
        }),
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['driver_id', 'user', 'phone', 'license_number', 'status', 'total_moves', 'average_rating']
    list_filter = ['status', 'is_active', 'hire_date']
    search_fields = ['driver_id', 'user__first_name', 'user__last_name', 'license_number', 'phone']
    readonly_fields = ['date_created']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'driver_id', 'phone', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('License Information', {
            'fields': ('license_number', 'license_expiry', 'cdl_class')
        }),
        ('Employment', {
            'fields': ('hire_date', 'status', 'hourly_rate')
        }),
        ('Performance', {
            'fields': ('total_moves', 'average_rating')
        }),
        ('System', {
            'fields': ('is_active', 'date_created')
        }),
    )

@admin.register(MovingCrew)
class MovingCrewAdmin(admin.ModelAdmin):
    list_display = ['crew_id', 'crew_leader', 'max_capacity_kg', 'is_active']
    list_filter = ['is_active', 'date_created']
    search_fields = ['crew_id', 'crew_leader__user__first_name', 'crew_leader__user__last_name']
    filter_horizontal = ['members', 'vehicles']

class InventoryTransferInline(admin.TabularInline):
    model = InventoryTransfer
    extra = 0

class MovingExpenseInline(admin.TabularInline):
    model = MovingExpense
    extra = 0

@admin.register(MovingAssignment)
class MovingAssignmentAdmin(admin.ModelAdmin):
    list_display = ['relocation_request', 'crew', 'status', 'scheduled_start_date', 'actual_start_date']
    list_filter = ['status', 'scheduled_start_date', 'requires_special_equipment']
    search_fields = ['relocation_request__request_id', 'crew__crew_id']
    readonly_fields = ['date_created', 'date_updated']
    inlines = [InventoryTransferInline, MovingExpenseInline]
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('relocation_request', 'crew', 'status')
        }),
        ('Scheduling', {
            'fields': ('scheduled_start_date', 'scheduled_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Route Information', {
            'fields': ('estimated_distance_km', 'actual_distance_km', 'estimated_duration_hours', 'actual_duration_hours')
        }),
        ('Special Requirements', {
            'fields': ('requires_special_equipment', 'special_equipment_notes')
        }),
        ('Additional Information', {
            'fields': ('notes', 'date_created', 'date_updated')
        }),
    )

@admin.register(InventoryTransfer)
class InventoryTransferAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'item_name', 'room_from', 'room_to', 'status', 'is_fragile', 'damage_reported']
    list_filter = ['status', 'is_fragile', 'requires_disassembly', 'damage_reported']
    search_fields = ['assignment__relocation_request__request_id', 'item_name', 'room_from', 'room_to']
    readonly_fields = ['date_created']

@admin.register(MovingExpense)
class MovingExpenseAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'expense_type', 'amount', 'date_incurred', 'submitted_by', 'is_approved']
    list_filter = ['expense_type', 'is_approved', 'date_incurred']
    search_fields = ['assignment__relocation_request__request_id', 'description']
    readonly_fields = ['date_created']
