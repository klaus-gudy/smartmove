from django.contrib import admin
from .models import Property, PropertyImage, PropertyInventory

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class PropertyInventoryInline(admin.TabularInline):
    model = PropertyInventory
    extra = 0

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['property_id', 'owner', 'property_type', 'city', 'state', 'bedrooms', 'bathrooms', 'square_feet', 'is_active']
    list_filter = ['property_type', 'is_active', 'city', 'state', 'has_elevator', 'has_parking']
    search_fields = ['property_id', 'owner__first_name', 'owner__last_name', 'address', 'city']
    readonly_fields = ['date_created', 'date_updated']
    inlines = [PropertyImageInline, PropertyInventoryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('property_id', 'owner', 'property_type')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_feet', 'floor_number', 'has_elevator', 'has_parking', 'has_storage')
        }),
        ('Access Information', {
            'fields': ('access_instructions', 'key_location', 'contact_person', 'contact_phone')
        }),
        ('Status', {
            'fields': ('is_active', 'date_created', 'date_updated')
        }),
    )

@admin.register(PropertyInventory)
class PropertyInventoryAdmin(admin.ModelAdmin):
    list_display = ['property', 'room', 'item_name', 'condition', 'is_fragile', 'estimated_value']
    list_filter = ['condition', 'is_fragile', 'requires_special_handling', 'property__property_type']
    search_fields = ['property__property_id', 'item_name', 'room', 'description']
    readonly_fields = ['date_created']
