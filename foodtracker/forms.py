from django import forms
from .models import Food, Image, WaterIntake, WaterGoal
from django.utils import timezone

class WaterIntakeForm(forms.ModelForm):
    """
    ModelForm for logging daily water intake
    """
    class Meta:
        model = WaterIntake
        fields = ['glasses']
        widgets = {
            'glasses': forms.NumberInput(attrs={
                'min': 0,
                'max': 50,
                'step': 1,
                'class': 'form-control',
                'placeholder': 'Number of glasses today'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['glasses'].label = "Glasses Consumed"

class WaterGoalForm(forms.ModelForm):
    """
    ModelForm for setting water consumption goals and reminders
    """
    class Meta:
        model = WaterGoal
        fields = ['daily_goal', 'reminder_enabled', 'reminder_interval']
        widgets = {
            'daily_goal': forms.NumberInput(attrs={
                'min': 1,
                'max': 20,
                'step': 1,
                'class': 'form-control',
                'placeholder': 'Daily glass goal'
            }),
            'reminder_interval': forms.NumberInput(attrs={
                'min': 30,
                'max': 240,
                'step': 15,
                'class': 'form-control',
                'placeholder': 'Minutes between reminders'
            }),
            'reminder_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['daily_goal'].label = "Daily Glass Goal"
        self.fields['reminder_interval'].label = "Reminder Interval (minutes)"
        self.fields['reminder_enabled'].label = "Enable Reminders"

class FoodForm(forms.ModelForm):
    """
    ModelForm for creating/editing food items
    """
    class Meta:
        model = Food
        fields = ['food_name', 'quantity', 'calories', 'fat', 
                 'carbohydrates', 'protein', 'category']
        widgets = {
            'food_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Food name'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantity in grams'
            }),
            'calories': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calories'
            }),
            'fat': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fat (g)'
            }),
            'carbohydrates': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Carbs (g)'
            }),
            'protein': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Protein (g)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ImageForm(forms.ModelForm):
    """
    ModelForm for uploading food images
    """
    class Meta:
        model = Image
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = "Upload Food Image"