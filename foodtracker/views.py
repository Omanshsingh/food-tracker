from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
from django.core.serializers.json import DjangoJSONEncoder

from .models import User, Food, FoodCategory, FoodLog, Image, Weight, FavoriteFood, WaterIntake, WaterGoal
from .forms import FoodForm, ImageForm, WaterIntakeForm, WaterGoalForm

# ======================
# WATER TRACKING VIEWS
# ======================

@login_required
def water_tracker_view(request):
    """Main water tracking dashboard"""
    today = timezone.now().date()
    
    # Get or create today's water intake
    water_intake, created = WaterIntake.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'glasses': 0}
    )
    
    # Get water goal (created via signal)
    water_goal = request.user.water_goal
    
    # Calculate progress percentage
    progress = min(100, (water_intake.glasses / water_goal.daily_goal) * 100) if water_goal.daily_goal else 0
    
    # Calculate remaining glasses
    remaining = max(0, water_goal.daily_goal - water_intake.glasses)
    
    # Get weekly data and prepare for template
    weekly_data = get_weekly_water_data(request.user)
    
    # Prepare chart data
    chart_labels = [item['date'].strftime('%Y-%m-%d') for item in weekly_data]
    chart_intake = [item['glasses'] for item in weekly_data]
    chart_goal = weekly_data[0]['goal'] if weekly_data else 0
    
    context = {
        'categories': FoodCategory.objects.all(),
        'water_intake': water_intake,
        'water_goal': water_goal,
        'progress': progress,
        'remaining': remaining,
        'today': today,
        'weekly_data': weekly_data,
        'chart_labels': chart_labels,
        'chart_intake': chart_intake,
        'chart_goal': chart_goal,
        'weekly_data_json': json.dumps(weekly_data, cls=DjangoJSONEncoder),
        'water_history': WaterIntake.objects.filter(user=request.user).order_by('-date')[:5]
    }
    return render(request, 'water_tracker.html', context)

@login_required
def log_water(request):
    """Log water intake via AJAX or form submission"""
    today = timezone.now().date()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        water_intake, created = WaterIntake.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'glasses': 0}
        )
        
        if action == 'add':
            water_intake.glasses += 1
        elif action == 'remove' and water_intake.glasses > 0:
            water_intake.glasses -= 1
        
        water_intake.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'glasses': water_intake.glasses,
                'progress': min(100, (water_intake.glasses / request.user.water_goal.daily_goal) * 100)
            })
    
    return redirect('water_tracker')

@login_required
def water_settings_view(request):
    """Update water goal and reminder settings"""
    water_goal = request.user.water_goal
    
    if request.method == 'POST':
        form = WaterGoalForm(request.POST, instance=water_goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Water settings updated successfully!')
            return redirect('water_settings')
    else:
        form = WaterGoalForm(instance=water_goal)
    
    context = {
        'categories': FoodCategory.objects.all(),
        'form': form,
    }
    return render(request, 'water_settings.html', context)

@login_required
def water_history_view(request):
    """View historical water intake data"""
    water_intakes = WaterIntake.objects.filter(user=request.user).order_by('-date')
    
    # Date filtering
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    
    if date_from:
        water_intakes = water_intakes.filter(date__gte=date_from)
    if date_to:
        water_intakes = water_intakes.filter(date__lte=date_to)
    
    # Pagination
    paginator = Paginator(water_intakes, 10)
    page = request.GET.get('page')
    
    try:
        water_intakes = paginator.page(page)
    except PageNotAnInteger:
        water_intakes = paginator.page(1)
    except EmptyPage:
        water_intakes = paginator.page(paginator.num_pages)
    
    context = {
        'categories': FoodCategory.objects.all(),
        'water_intakes': water_intakes,
    }
    return render(request, 'water_history.html', context)

@login_required
def export_water_data(request):
    """Export water data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="water_intake_history.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Glasses Consumed', 'Daily Goal', 'Percentage Met'])
    
    water_intakes = WaterIntake.objects.filter(user=request.user).order_by('-date')
    water_goal = request.user.water_goal.daily_goal
    
    for intake in water_intakes:
        percentage = (intake.glasses / water_goal) * 100 if water_goal else 0
        writer.writerow([
            intake.date.strftime('%Y-%m-%d'),
            intake.glasses,
            water_goal,
            f"{min(100, percentage):.1f}%"
        ])
    
    return response

def get_weekly_water_data(user):
    """Get weekly water intake data for charts"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)
    
    water_intakes = WaterIntake.objects.filter(
        user=user,
        date__range=[week_ago, today]
    ).order_by('date')
    
    # Create full week data even if some days are missing
    data = []
    goal = user.water_goal.daily_goal
    
    for i in range(7):
        current_date = week_ago + timedelta(days=i)
        intake = water_intakes.filter(date=current_date).first()
        glasses = intake.glasses if intake else 0
        met_goal = glasses >= goal if goal else False
        
        data.append({
            'date': current_date,
            'glasses': glasses,
            'goal': goal,
            'met_goal': met_goal,
            'percentage': min(100, (glasses / goal * 100)) if goal else 0,
        })
    
    return data

# [Rest of your existing views (authentication, food management, weight tracking, etc.) 
# remain exactly the same as in your original file]

# ======================
# AUTHENTICATION VIEWS
# ======================

def index(request):
    """Home page view"""
    return food_list_view(request)

def register(request):
    """User registration"""
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

# ======================
# FOOD MANAGEMENT VIEWS
# ======================

@login_required
def dashboard(request):
    """Main dashboard view"""
    context = {
        'food_logs': FoodLog.objects.filter(user=request.user).order_by('-consumed_at'),
        'favorite_foods': FavoriteFood.objects.filter(user=request.user),
        'categories': FoodCategory.objects.all()
    }
    return render(request, 'dashboard.html', context)

@login_required
def food_log_view(request):
    """Handle food logging"""
    if request.method == 'POST':
        food_id = request.POST.get('food_consumed')
        if food_id:
            try:
                food = Food.objects.get(id=food_id)
                FoodLog.objects.create(
                    user=request.user,
                    food_consumed=food
                )
                return redirect('food_log')
            except Food.DoesNotExist:
                messages.error(request, "Selected food not found")
    
    context = {
        'categories': FoodCategory.objects.all(),
        'foods': Food.objects.all(),
        'user_food_log': FoodLog.objects.filter(user=request.user).order_by('-consumed_at')
    }
    return render(request, 'food_log.html', context)

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

# ======================
# WEIGHT TRACKING VIEWS
# ======================

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

# ======================
# CATEGORY VIEWS
# ======================

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

# ======================
# FAVORITE FOODS VIEWS
# ======================

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
    except FavoriteFood.DoesNotExist:
        messages.error(request, "Favorite food not found")
    
    return redirect('dashboard')