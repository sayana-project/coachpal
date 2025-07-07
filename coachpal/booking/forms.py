from django import forms
from .models import Booking
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        exclude = ['user']  # Exclure le champ user du formulaire
        fields = '__all__'
        widgets = {
            'appointment_datetime': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'min': '2024-01-01T08:30',
                    'step': 600,  # intervalle de 10 min
                    'class': 'form-control',
                }
            )
        }

    def clean_appointment_datetime(self):
        dt = self.cleaned_data['appointment_datetime']

        if dt.weekday() > 4:
            raise forms.ValidationError("Les réservations sont disponibles uniquement du lundi au vendredi.")

        morning = datetime.time(8, 30), datetime.time(12, 30)
        afternoon = datetime.time(13, 30), datetime.time(17, 30)

        if not (morning[0] <= dt.time() <= morning[1] or afternoon[0] <= dt.time() <= afternoon[1]):
            raise forms.ValidationError("Les horaires valides sont 08h30-12h30 et 13h30-17h30.")

        return dt