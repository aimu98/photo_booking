from django.contrib import admin
from .models import Reservation, AvailableSlot

class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time')

admin.site.register(Reservation)  
admin.site.register(AvailableSlot, AvailableSlotAdmin) 

