from django.forms import ModelForm
from .models import Recipe

# Recipe Meal Planner Form
class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['day_of_the_week', 'meal_type', 'recipe_name', 'recipe_description']