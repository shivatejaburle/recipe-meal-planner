from django.db import models
from django.contrib.auth.models import User

# Recipe Model
class Recipe(models.Model):
    class Weekday(models.IntegerChoices):
        Monday = 1
        Tuesday = 2
        Wednesday = 3
        Thursday = 4
        Friday = 5
        Saturday = 6
        Sunday = 7
    day_of_the_week = models.IntegerField(choices=Weekday.choices)

    def get_weekday_label(self):
        return self.Weekday(self.day_of_the_week).label

    class MealType(models.IntegerChoices):
        Breakfast = 1
        Lunch = 2
        Dinner = 3
    meal_type = models.IntegerField(choices=MealType.choices)

    def get_meal_type_label(self):
        return self.MealType(self.meal_type).label

    recipe_name = models.CharField(max_length=100)
    recipe_description = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + "-" + str(self.get_weekday_label()) + "-" + str(self.get_meal_type_label())