from django import forms
from django.contrib.auth.models import User
from datetime import date as ddate, time as dtime, datetime, timedelta
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['objet','coach', 'date', 'time', 'firstname', 'lastname', 'email']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # utilisateur connecté
        super().__init__(*args, **kwargs)
        
        # Liste des dates (7 prochains jours ouvrés)
        today = ddate.today()
        dates = [today + timedelta(days=i) for i in range(1, 15)]
        weekdays = [d for d in dates if d.weekday() < 5]
        self.fields['date'].widget = forms.Select(
            choices=[(d, d.strftime("%A %d %B %Y")) for d in weekdays]
        )
        
        # Liste des coaches disponibles
        self.fields['coach'].queryset = User.objects.filter(groups__name='coach')
        
        # Liste des heures autorisées (8h30-12h30 et 13h30-17h30)
        slots = []
        for period in [(8, 30, 12, 30), (13, 30, 17, 30)]:
            start = dtime(hour=period[0], minute=period[1])
            end = dtime(hour=period[2], minute=period[3])
            current = datetime.combine(ddate.today(), start)
            while current.time() <= end:
                slots.append((
                    current.time().strftime('%H:%M'), 
                    current.time().strftime('%H:%M')
                ))
                current += timedelta(minutes=30)
        self.fields['time'].widget = forms.Select(choices=slots)
    
    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('date')
        appointment_time = cleaned_data.get('time')
        coach = cleaned_data.get('coach')
        
        if not appointment_date or not appointment_time or not coach:
            return cleaned_data
        
        # Convertir en datetime pour les calculs
        if isinstance(appointment_time, str):
            appointment_time = datetime.strptime(appointment_time, '%H:%M').time()
        
        appointment_datetime = datetime.combine(appointment_date, appointment_time)
        
        # 1. Vérifier les conflits exacts (même coach, même date, même heure)
        exact_conflict = Booking.objects.filter(
            coach=coach,
            date=appointment_date,
            time=appointment_time
        )
        
        # Exclure la réservation actuelle si on est en mode édition
        if self.instance and self.instance.pk:
            exact_conflict = exact_conflict.exclude(pk=self.instance.pk)
        
        if exact_conflict.exists():
            raise forms.ValidationError(
                f"Le coach {coach.get_full_name() or coach.username} a déjà une réservation à cette heure."
            )
        
        # 2. Vérifier l'intervalle de 10 minutes
        # Un RDV dure 30 minutes, donc on vérifie :
        # - 10 min avant le début
        # - Pendant les 30 min du RDV
        # - 10 min après la fin
        rdv_start = appointment_datetime
        rdv_end = appointment_datetime + timedelta(minutes=30)
        
        # Récupérer tous les RDV du coach ce jour-là
        existing_bookings = Booking.objects.filter(
            coach=coach,
            date=appointment_date
        )
        
        if self.instance and self.instance.pk:
            existing_bookings = existing_bookings.exclude(pk=self.instance.pk)
        
        for booking in existing_bookings:
            existing_start = datetime.combine(appointment_date, booking.time)
            existing_end = existing_start + timedelta(minutes=30)
            
            # Vérifier s'il y a moins de 10 minutes entre les créneaux
            time_diff_start = abs((rdv_start - existing_end).total_seconds() / 60)
            time_diff_end = abs((existing_start - rdv_end).total_seconds() / 60)
            
            # Vérifier les chevauchements ou intervalles trop courts
            if (rdv_start < existing_end and rdv_end > existing_start) or \
               (time_diff_start < 10 and rdv_start >= existing_end) or \
               (time_diff_end < 10 and existing_start >= rdv_end):
                raise forms.ValidationError(
                    f"Ce créneau est trop proche d'une autre réservation. "
                    f"Il faut au moins 10 minutes entre les rendez-vous."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        booking = super().save(commit=False)
        if self.user:
            booking.user = self.user
        if commit:
            booking.save()
        return booking