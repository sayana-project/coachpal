from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']  # Adaptez selon vos champs
    list_filter = ['created_at']
    search_fields = ['id']