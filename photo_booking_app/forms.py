from django import forms
from .models import Reservation , AvailableSlot
from datetime import timedelta, date
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['name','children_name', 'phone', 'date', 'start_time','end_time','plan','message']
        exclude = ['user', 'created_at']
        widgets = {
            'date': forms.SelectDateWidget, 
        }
    
    start_time = forms.ChoiceField(choices=[], required=True)
    end_time = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        slots = AvailableSlot.objects.order_by('start_time', 'end_time')
        start_choices = sorted(set((slot.start_time, slot.start_time.strftime('%H:%M')) for slot in slots))
        end_choices = sorted(set((slot.end_time, slot.end_time.strftime('%H:%M')) for slot in slots))

        self.fields['start_time'].choices = start_choices
        self.fields['end_time'].choices = end_choices
        
    def save(self, user=None, commit=True):
        reservation = super().save(commit=False)
        if user is not None:
            reservation.user = user
        if commit:
            reservation.save() 
        return reservation
            
class AvailableSlotForm(forms.ModelForm):
    class Meta:
        model = AvailableSlot
        fields = ['date', 'start_time', 'end_time']

class ReservationEditForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'start_time', 'end_time','plan', 'name', 'children_name']

    def clean_date(self):
        selected_date = self.cleaned_data['date']
        if selected_date < date.today() + timedelta(days=3):
            raise forms.ValidationError("予約の変更は3日前までしかできません。")
        return selected_date

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='名字')
    last_name = forms.CharField(max_length=30, required=True, label='名前')
    email = forms.EmailField(required=True, label='メールアドレス')

    class Meta:
        model = User
        fields = ('username', "email",'first_name', 'last_name', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user