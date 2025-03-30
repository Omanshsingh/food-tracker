from django import forms
from .models import Food, Image, WaterIntake, WaterGoal

class FoodForm(forms.ModelForm):
    """
    ModelForm for creating/editing food items
    """
    class Meta:
        model = Food
        fields = ['food_name', 'quantity', 'calories', 'fat', 
                 'carbohydrates', 'protein', 'category', 'description']
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
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the food and add your insights (nutrition, best time to eat, pairings, etc.)',  # Updated placeholder
                'rows': 4
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['description'].required = False

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
        self.fields['image'].required = False

class WaterIntakeForm(forms.ModelForm):
    class Meta:
        model = WaterIntake
        fields = ['glasses']
        widgets = {
            'glasses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            })
        }

class WaterGoalForm(forms.ModelForm):
    class Meta:
        model = WaterGoal
        fields = ['daily_goal', 'reminder_enabled', 'reminder_interval']
        widgets = {
            'daily_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'reminder_interval': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 30,
                'max': 240
            })
        }