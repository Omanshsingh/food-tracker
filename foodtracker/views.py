from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import User, Food, FoodCategory, FoodLog, Image, Weight, FavoriteFood, Streak
from .forms import FoodForm, ImageForm

# Main Streak View (Combined Dashboard)
@login_required
def streak_view(request):
    """Display the complete streak dashboard with history and achievements"""
    streak, created = Streak.objects.get_or_create(user=request.user)
    
    # Dashboard Data
    next_milestone = ((streak.current_streak // 5) + 1) * 5
    progress = (streak.current_streak % 5) * 20 if streak.current_streak > 0 else 0
    recent_logs = FoodLog.objects.filter(user=request.user).order_by('-consumed_at')[:5]
    
    # History Data - group logs by week
    weekly_logs = {}
    for log in FoodLog.objects.filter(user=request.user).order_by('-consumed_at'):
        week = log.consumed_at.isocalendar()[1]  # Get ISO week number
        weekly_logs.setdefault(week, []).append(log)
    
    # Achievements Data
    milestones = {
        '5_days': streak.longest_streak >= 5,
        '10_days': streak.longest_streak >= 10,
        '30_days': streak.longest_streak >= 30,
        '100_days': streak.longest_streak >= 100,
    }
    
    context = {
        'current_streak': streak.current_streak,
        'longest_streak': streak.longest_streak,
        'last_active': streak.last_activity_date,
        'next_milestone': next_milestone,
        'progress': progress,
        'recent_logs': recent_logs,
        'weekly_logs': weekly_logs,
        'milestones': milestones,
        'categories': FoodCategory.objects.all()
    }
    return render(request, 'streaks/streak.html', context)

# Updated Existing Views with Streak Integration
@login_required
def dashboard(request):
    """Main dashboard view with streak display"""
    streak, created = Streak.objects.get_or_create(user=request.user)
    context = {
        'food_logs': FoodLog.objects.filter(user=request.user).order_by('-consumed_at'),
        'streak': streak.current_streak,
        'favorite_foods': FavoriteFood.objects.filter(user=request.user),
        'categories': FoodCategory.objects.all()
    }
    return render(request, 'dashboard.html', context)

@login_required
def food_log_view(request):
    """Handle food logging with streak updates"""
    if request.method == 'POST':
        food_id = request.POST.get('food_consumed')
        if food_id:
            try:
                food = Food.objects.get(id=food_id)
                FoodLog.objects.create(
                    user=request.user,
                    food_consumed=food
                )
                
                # Update streak
                streak, created = Streak.objects.get_or_create(user=request.user)
                current_streak = streak.update_streak()
                
                # Celebration for milestones
                if current_streak % 5 == 0:
                    messages.success(request, f"🔥 Amazing! {current_streak}-day streak!")
                    
                return redirect('food_log')
                
            except Food.DoesNotExist:
                messages.error(request, "Selected food not found")
    
    context = {
        'categories': FoodCategory.objects.all(),
        'foods': Food.objects.all(),
        'user_food_log': FoodLog.objects.filter(user=request.user).order_by('-consumed_at')
    }
    return render(request, 'food_log.html', context)

# Authentication Views
def index(request):
    """Home page view"""
    return food_list_view(request)

def register(request):
    """User registration with automatic streak creation"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        
        if password != confirmation:
            return render(request, 'register.html', {
                'message': 'Passwords must match.',
                'categories': FoodCategory.objects.all()
            })

        try:
            user = User.objects.create_user(username, email, password)
            Streak.objects.create(user=user)  # Create streak for new user
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            return render(request, 'register.html', {
                'message': 'Username already taken.',
                'categories': FoodCategory.objects.all()
            })
    
    return render(request, 'register.html', {
        'categories': FoodCategory.objects.all()
    })

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        
        return render(request, 'login.html', {
            'message': 'Invalid username/password',
            'categories': FoodCategory.objects.all()
        })
    
    return render(request, 'login.html', {
        'categories': FoodCategory.objects.all()
    })

def logout_view(request):
    """User logout view"""
    logout(request)
    return HttpResponseRedirect(reverse('index'))

# Food Management Views
def food_list_view(request):
    """List all available foods"""
    foods = Food.objects.all()
    for food in foods:
        food.image = food.get_images.first()

    paginator = Paginator(foods, 4)
    page = request.GET.get('page', 1)
    
    try:
        pages = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        pages = paginator.page(1)

    context = {
        'categories': FoodCategory.objects.all(),
        'foods': foods,
        'pages': pages,
        'title': 'Food List'
    }
    return render(request, 'index.html', context)

def food_details_view(request, food_id):
    """Show details for a specific food"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    food = Food.objects.get(id=food_id)
    context = {
        'categories': FoodCategory.objects.all(),
        'food': food,
        'images': food.get_images.all(),
    }
    return render(request, 'food.html', context)

@login_required
def food_add_view(request):
    """Add new food to database"""
    ImageFormSet = forms.modelformset_factory(Image, form=ImageForm, extra=2)
    
    if request.method == 'POST':
        food_form = FoodForm(request.POST, request.FILES)
        image_form = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())

        if food_form.is_valid() and image_form.is_valid():
            new_food = food_form.save()
            
            for form in image_form.cleaned_data:
                if form and form.get('image'):
                    Image.objects.create(food=new_food, image=form['image'])
            
            return render(request, 'food_add.html', {
                'categories': FoodCategory.objects.all(),
                'food_form': FoodForm(),
                'image_form': ImageFormSet(queryset=Image.objects.none()),
                'success': True
            })
    
    context = {
        'categories': FoodCategory.objects.all(),
        'food_form': FoodForm(),
        'image_form': ImageFormSet(queryset=Image.objects.none()),
    }
    return render(request, 'food_add.html', context)

@login_required
def food_log_delete(request, food_id):
    """Delete a food log entry"""
    food_consumed = FoodLog.objects.filter(id=food_id, user=request.user)
    
    if request.method == 'POST':
        food_consumed.delete()
        return redirect('food_log')
    
    return render(request, 'food_log_delete.html', {
        'categories': FoodCategory.objects.all()
    })

# Weight Tracking Views
@login_required
def weight_log_view(request):
    """Log and view weight entries"""
    if request.method == 'POST':
        weight = request.POST['weight']
        entry_date = request.POST['date'] or timezone.now().date()
        Weight.objects.create(
            user=request.user,
            weight=weight,
            entry_date=entry_date
        )
    
    context = {
        'categories': FoodCategory.objects.all(),
        'user_weight_log': Weight.objects.filter(user=request.user).order_by('-entry_date')
    }
    return render(request, 'user_profile.html', context)

@login_required
def weight_log_delete(request, weight_id):
    """Delete a weight log entry"""
    weight_recorded = Weight.objects.filter(id=weight_id, user=request.user)
    
    if request.method == 'POST':
        weight_recorded.delete()
        return redirect('weight_log')
    
    return render(request, 'weight_log_delete.html', {
        'categories': FoodCategory.objects.all()
    })

# Category Views
def categories_view(request):
    """List all food categories"""
    return render(request, 'categories.html', {
        'categories': FoodCategory.objects.all()
    })

def category_details_view(request, category_name):
    """Show foods in a specific category"""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    category = FoodCategory.objects.get(category_name=category_name)
    foods = Food.objects.filter(category=category)
    
    for food in foods:
        food.image = food.get_images.first()

    paginator = Paginator(foods, 4)
    page = request.GET.get('page', 1)
    
    try:
        pages = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        pages = paginator.page(1)

    context = {
        'categories': FoodCategory.objects.all(),
        'foods': foods,
        'foods_count': foods.count(),
        'pages': pages,
        'title': category.category_name
    }
    return render(request, 'food_category.html', context)

# Favorite Foods Views
@login_required
def add_favorite_food(request):
    """Add a food to favorites"""
    if request.method == 'POST':
        name = request.POST.get('name')
        calories = request.POST.get('calories')
        if name and calories:
            FavoriteFood.objects.create(
                user=request.user,
                name=name,
                calories=calories
            )
    return redirect('dashboard')

@login_required
def quick_add_favorite(request, food_id):
    """Quick log a favorite food"""
    try:
        favorite = FavoriteFood.objects.get(id=food_id, user=request.user)
        food = Food.objects.filter(food_name=favorite.name).first()
        
        if food:
            FoodLog.objects.create(
                user=request.user,
                food_consumed=food,
                consumed_at=timezone.now()
            )
            # Update streak
            streak, created = Streak.objects.get_or_create(user=request.user)
            streak.update_streak()
            
    except FavoriteFood.DoesNotExist:
        messages.error(request, "Favorite food not found")
    
    return redirect('dashboard')