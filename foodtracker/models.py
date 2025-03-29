from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    def __str__(self):
        return f'{self.username}'

class FoodCategory(models.Model):
    category_name = models.CharField(max_length=50)
    icon = models.CharField(max_length=30, default='tag')

    class Meta:
        verbose_name = 'Food Category'
        verbose_name_plural = 'Food Categories'

    def __str__(self):
        return f'{self.category_name}'

    @property
    def count_food_by_category(self):
        return Food.objects.filter(category=self).count()

class Food(models.Model):
    food_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=7, decimal_places=2, default=100.00)
    calories = models.IntegerField(default=0)
    fat = models.DecimalField(max_digits=7, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=7, decimal_places=2)
    protein = models.DecimalField(max_digits=7, decimal_places=2)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='food_category')

    def __str__(self):
        return f'{self.food_name} - category: {self.category}'

class Image(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='get_images')
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f'{self.image}'

class Streak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(default=timezone.now)

    def update_streak(self):
        today = timezone.now().date()
        if self.last_activity_date == today:
            return self.current_streak
        
        if (today - self.last_activity_date).days == 1:
            self.current_streak += 1
        else:
            self.current_streak = 1
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_activity_date = today
        self.save()
        return self.current_streak

    def __str__(self):
        return f"{self.user.username}'s streak: {self.current_streak} days (Longest: {self.longest_streak})"

class FoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_consumed = models.ForeignKey(Food, on_delete=models.CASCADE)
    consumed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Food Log'
        verbose_name_plural = 'Food Logs'

    def __str__(self):
        return f'{self.user.username} - {self.food_consumed.food_name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if hasattr(self.user, 'streak'):
            self.user.streak.update_streak()

class Weight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=7, decimal_places=2)
    entry_date = models.DateField()

    class Meta:
        verbose_name = 'Weight'
        verbose_name_plural = 'Weight'

    def __str__(self):
        return f'{self.user.username} - {self.weight} kg on {self.entry_date}'

class FavoriteFood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Favorite Food'
        verbose_name_plural = 'Favorite Foods'

    def __str__(self):
        return f'{self.user.username} - {self.food.food_name}'

class WaterIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_intakes')
    date = models.DateField(default=timezone.now)
    glasses = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    
    class Meta:
        verbose_name = 'Water Intake'
        verbose_name_plural = 'Water Intakes'
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} - {self.glasses} glasses on {self.date}'

class WaterGoal(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='water_goal'
    )
    daily_goal = models.PositiveIntegerField(
        default=8,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    reminder_enabled = models.BooleanField(default=False)
    reminder_interval = models.PositiveIntegerField(
        default=60,  # minutes
        validators=[MinValueValidator(30), MaxValueValidator(240)]
    )
    last_reminder_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Water Goal'
        verbose_name_plural = 'Water Goals'

    def __str__(self):
        return f'{self.user.username} - {self.daily_goal} glasses daily'

# Signals
@receiver(post_save, sender=User)
def create_user_streak(sender, instance, created, **kwargs):
    if created:
        Streak.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_user_water_goal(sender, instance, created, **kwargs):
    if created:
        WaterGoal.objects.create(
            user=instance,
            daily_goal=8,
            reminder_enabled=False,
            reminder_interval=60
        )