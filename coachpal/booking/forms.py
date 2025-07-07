from django import forms
from .models import Booking
from datetime import datetime, timedelta, time as dtime, date as ddate
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User

#séance
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['coach','date', 'time', 'firstname', 'lastname', 'email']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # pour accéder à l'utilisateur connecté
        super().__init__(*args, **kwargs)

        # Liste des dates (7 prochains jours ouvrés)
        today = ddate.today()
        dates = [today + timedelta(days=i) for i in range(1, 15)]
        weekdays = [d for d in dates if d.weekday() < 5]
        self.fields['date'].widget = forms.Select(choices=[(d, d.strftime("%A %d %B %Y")) for d in weekdays])
        self.fields['coach'].queryset = User.objects.filter(groups__name='coach')

        #Liste des heures autorisées (8h30-12h30 et 13h30-17h30)
        slots = []
        for period in [(8, 30, 12, 30), (13, 30, 17, 30)]:
            start = dtime(hour=period[0], minute=period[1])
            end = dtime(hour=period[2], minute=period[3])
            current = datetime.combine(ddate.today(), start)
            while current.time() <= end:
                slots.append((current.time().strftime('%H:%M'), current.time().strftime('%H:%M')))
                current += timedelta(minutes=30)
        self.fields['time'].widget = forms.Select(choices=slots)

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('date')
        appointment_time = cleaned_data.get('time')

        if not appointment_date or not appointment_time:
            return cleaned_data

        start_time = datetime.combine(appointment_date, appointment_time)
        end_time = start_time + timedelta(minutes=30)

        # Créneau interdit si trop proche d’un autre avec ce coach (10 min avant ou après)
        lower_bound = start_time - timedelta(minutes=40)
        upper_bound = start_time + timedelta(minutes=40)

        coach = self.user.profile.coach
        conflict = Booking.objects.filter(
            coach=coach,
            date=appointment_date,
            time__gte=(lower_bound.time()),
            time__lt=(upper_bound.time())
        ).exists()

        if conflict:
            raise forms.ValidationError("Ce créneau n'est pas disponible. Merci d'en choisir un autre.")

        return cleaned_data