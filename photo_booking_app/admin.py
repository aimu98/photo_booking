from django.contrib import admin
from .models import Reservation, AvailableSlot

class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time')

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'children_name', 'date', 'start_time', 'end_time', 'plan')
    list_filter = ('date', 'plan')  # status を削除
    search_fields = ('name', 'children_name', 'email', 'phone')

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(AvailableSlot, AvailableSlotAdmin)
