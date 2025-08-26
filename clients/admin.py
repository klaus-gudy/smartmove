from django.contrib import admin
from .models import Client, ClientDocument

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'first_name', 'last_name', 'company_name', 'client_type', 'email', 'phone', 'city', 'is_active', 'date_created']
    list_filter = ['client_type', 'is_active', 'city', 'state', 'date_created']
    search_fields = ['client_id', 'first_name', 'last_name', 'company_name', 'email', 'phone']
    readonly_fields = ['date_created', 'date_updated']
    fieldsets = (
        ('Basic Information', {
            'fields': ('client_id', 'client_type', 'user')
        }),
        ('Personal/Company Details', {
            'fields': ('first_name', 'last_name', 'company_name', 'email', 'phone')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Status', {
            'fields': ('is_active', 'date_created', 'date_updated')
        }),
    )

@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    list_display = ['client', 'document_type', 'document_name', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['client__first_name', 'client__last_name', 'document_name']
    readonly_fields = ['uploaded_at']
