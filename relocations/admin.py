from django.contrib import admin
from .models import RelocationRequest, RelocationQuote, RelocationTimeline

class RelocationQuoteInline(admin.TabularInline):
    model = RelocationQuote
    extra = 0
    readonly_fields = ['total_cost']

class RelocationTimelineInline(admin.TabularInline):
    model = RelocationTimeline
    extra = 0
    readonly_fields = ['date_created']

@admin.register(RelocationRequest)
class RelocationRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'client', 'relocation_type', 'status', 'priority', 'preferred_date', 'assigned_to', 'estimated_cost']
    list_filter = ['status', 'priority', 'relocation_type', 'requires_packing', 'requires_storage', 'date_created']
    search_fields = ['request_id', 'client__first_name', 'client__last_name', 'origin_property__address']
    readonly_fields = ['date_created', 'date_updated']
    inlines = [RelocationQuoteInline, RelocationTimelineInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('request_id', 'client', 'relocation_type', 'status', 'priority', 'assigned_to')
        }),
        ('Properties', {
            'fields': ('origin_property', 'destination_property')
        }),
        ('Destination Address (if no property record)', {
            'fields': ('destination_address', 'destination_city', 'destination_state', 'destination_zip', 'destination_country'),
            'classes': ['collapse']
        }),
        ('Scheduling', {
            'fields': ('preferred_date', 'alternative_date', 'scheduled_date', 'actual_start_date', 'actual_completion_date')
        }),
        ('Services Required', {
            'fields': ('requires_packing', 'requires_unpacking', 'requires_storage', 'requires_insurance', 'requires_cleaning')
        }),
        ('Cost Information', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'notes', 'date_created', 'date_updated')
        }),
    )

@admin.register(RelocationQuote)
class RelocationQuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'relocation_request', 'status', 'total_cost', 'valid_until', 'date_created']
    list_filter = ['status', 'date_created', 'valid_until']
    search_fields = ['quote_number', 'relocation_request__request_id', 'relocation_request__client__first_name']
    readonly_fields = ['total_cost', 'date_created']
    
    fieldsets = (
        ('Quote Information', {
            'fields': ('quote_number', 'relocation_request', 'status', 'valid_until')
        }),
        ('Cost Breakdown', {
            'fields': ('base_cost', 'packing_cost', 'transportation_cost', 'insurance_cost', 'storage_cost', 'additional_services_cost', 'tax_amount', 'total_cost')
        }),
        ('Terms', {
            'fields': ('terms_and_conditions',)
        }),
        ('Dates', {
            'fields': ('date_created', 'date_sent', 'date_responded')
        }),
    )

@admin.register(RelocationTimeline)
class RelocationTimelineAdmin(admin.ModelAdmin):
    list_display = ['relocation_request', 'milestone_type', 'scheduled_datetime', 'actual_datetime', 'is_completed', 'updated_by']
    list_filter = ['milestone_type', 'is_completed', 'scheduled_datetime']
    search_fields = ['relocation_request__request_id', 'description']
    readonly_fields = ['date_created']
