from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from .forms import BookingForm
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import Group
from .models import Booking,Profile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

def acceuil(request):
    return render(request, 'booking/acceuil.html')

def redirect_dashboard(request):
    user = request.user
    if user.groups.filter(name='coach').exists():
        return redirect('booking:dashboard_coach')
    elif user.groups.filter(name='client').exists():
        return redirect('booking:dashboard_client')
    else:
        return redirect('booking:acceuil')

@login_required
def dashboard_coach(request):
    if not request.user.groups.filter(name='coach').exists():
        return HttpResponseForbidden("Accès réservé aux coachs")
    
    reservations = Booking.objects.filter(coach=request.user).order_by('date', 'time')
    today = date.today()
    upcoming_reservations = reservations.filter(date__gte=today)
    past_reservations = reservations.filter(date__lt=today)
    
    return render(request, 'booking/dashboard_coach.html', {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
        'today': today
    })

@login_required
def dashboard_client(request):
    if not request.user.groups.filter(name='client').exists():
        return HttpResponseForbidden("Accès réservé aux clients")
    today = date.today()
    reservations = Booking.objects.filter(user=request.user).order_by('-date', '-time')
    upcoming_reservations = reservations.filter(date__gte=today)
    past_reservations = reservations.filter(date__lt=today)

    
    return render(request, 'booking/dashboard_client.html', {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations,
        'today': today
    })

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            return redirect('booking:success')
    else:
        form = BookingForm(user=request.user)
    return render(request, 'booking/form.html', {'form': form})

def success(request):
    return render(request, 'booking/success.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            client_group, created = Group.objects.get_or_create(name='client')
            user.groups.add(client_group)
            login(request, user)
            return redirect('booking:acceuil')
        else:
            messages.error(request, "Erreur dans le formulaire. Veuillez corriger les champs.")
    else:
        form = UserCreationForm()
    return render(request, 'booking/signup.html', {'form': form})

@require_POST
def custom_logout(request):
    logout(request)
    return redirect('booking:acceuil')

@login_required
def modifier_reservation(request, pk):
    reservation = get_object_or_404(Booking, id=pk)
    
    if not (reservation.user == request.user or reservation.coach == request.user):
        return HttpResponseForbidden("Vous n'avez pas le droit de modifier cette réservation")
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('booking:dashboard_client' if request.user.groups.filter(name='client').exists() else 'booking:dashboard_coach')
    else:
        form = BookingForm(instance=reservation, user=request.user)
    
    return render(request, 'booking/modifier_reservation.html', {'form': form, 'reservation': reservation})

@login_required
def supprimer_reservation(request, pk):
    reservation = get_object_or_404(Booking, id=pk)
    
    if not (reservation.user == request.user or reservation.coach == request.user):
        return HttpResponseForbidden("Vous n'avez pas le droit de supprimer cette réservation")
    
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Réservation supprimée avec succès.")
        return redirect('booking:dashboard_client' if request.user.groups.filter(name='client').exists() else 'booking:dashboard_coach')
    
    return render(request, 'booking/confirmer_suppression.html', {'reservation': reservation})

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)