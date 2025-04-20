from django import forms
from .models import Reservation , AvailableSlot
from datetime import timedelta, date

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name','children_name', 'email', 'phone', 'date', 'start_time', 'end_time','plan','message']
        widgets = {
            'date': forms.SelectDateWidget, 
        }
    
    start_time = forms.ChoiceField(choices=[], required=True)
    end_time = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        slots = AvailableSlot.objects.order_by('start_time')
        start_choices = sorted(set((slot.start_time, slot.start_time.strftime('%H:%M')) for slot in slots))
        end_choices = sorted(set((slot.end_time, slot.end_time.strftime('%H:%M')) for slot in slots))

        self.fields['start_time'].choices = start_choices
        self.fields['end_time'].choices = end_choices
            
class AvailableSlotForm(forms.ModelForm):
    class Meta:
        model = AvailableSlot
        fields = ['date', 'start_time', 'end_time']

class ReservationEditForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'start_time', 'end_time', 'plan', 'name', 'children_name']

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        if selected_date < date.today() + timedelta(days=3):
            raise forms.ValidationError("予約の変更は3日前までしかできません。")
        return selected_date

