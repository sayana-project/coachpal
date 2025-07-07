from django.contrib import messages
from django.shortcuts import render, redirect
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
    return render(request, 'booking/dashboard_coach.html', {'reservations': reservations})

@login_required
def dashboard_client(request):
    if not request.user.groups.filter(name='client').exists():
        return HttpResponseForbidden("Accès réservé aux clients")
    reservations = Booking.objects.filter(client=request.user).order_by('date', 'time')
    return render(request, 'booking/dashboard_client.html',{'reservations': reservations})

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

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
from django.contrib.auth.decorators import user_passes_test

def group_required(group_name):
    return user_passes_test(lambda u: u.is_authenticated and u.groups.filter(name=group_name).exists())

@group_required('coach')
def dashboard_coach(request):
    return render(request, 'booking/dashboard_coach.html')

@group_required('client')
def dashboard_client(request):
    return render(request, 'booking/dashboard_client.html')