from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from planner.models import Recipe
from planner.forms import RecipeForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin

# Home Page
class IndexView(TemplateView):
    template_name = 'planner/index.html'

# View Recipes
class RecipeList(LoginRequiredMixin, ListView):
    model = Recipe
    http_method_names = ['get']
    # queryset = Recipe.objects.all()
    context_object_name = 'recipe_list'
    template_name = 'planner/recipe_list.html'

    def get_queryset(self):
        # Filter by logged in user and order by day_of_the_week and meal_type
        queryset = self.model.objects.filter(user=self.request.user).order_by('day_of_the_week', 'meal_type')
        return queryset

# Create Recipe
class RecipeCreate(LoginRequiredMixin, CreateView):
    model = Recipe
    fields = ['day_of_the_week', 'meal_type', 'recipe_name', 'recipe_description']
    http_method_names = ['get', 'post']
    context_object_name = 'form'
    template_name = 'planner/recipe_form.html'
    success_url = reverse_lazy('planner:recipe_list')

    def post(self, request, *args, **kwargs):
        form = RecipeForm(request.POST)
        if not form.is_valid():
            context = {
                'form':form
            }
            return render(request, self.template_name, context)
        
        obj = form.save(commit = False)

        # Filter by logged in user
        queryset = Recipe.objects.filter(user=self.request.user, day_of_the_week=obj.day_of_the_week, meal_type=obj.meal_type)

        # Check the record is exist or not before you create
        if queryset.exists():
            msg = "Already a recipe is scheduled with selected day and time. So, please update the record with required changes."
            messages.info(request, msg)
            return redirect(reverse_lazy('planner:recipe_update', kwargs={'pk' : queryset[0].id}))
        else:
            # Add the owner of the record
            obj.user = self.request.user
            obj.save()
            messages.success(request, "Your recipe has been created successfully.")
        
        return redirect(self.success_url)
    
# Generate PDF
class RecipeListPdf(LoginRequiredMixin, ListView):
    model = Recipe
    http_method_names = ['get']
    context_object_name = 'recipe_list'
    template_name = 'planner/recipe_list_pdf.html'

    def get_queryset(self):
        # Filter by logged in user and order by day_of_the_week and meal_type
        queryset = self.model.objects.filter(user=self.request.user).order_by('day_of_the_week', 'meal_type')
        return queryset
    
# Edit or Update Recipe
class RecipeUpdate(LoginRequiredMixin, UpdateView):
    model = Recipe
    fields = ['day_of_the_week', 'meal_type', 'recipe_name', 'recipe_description']
    template_name = 'planner/recipe_form.html'
    success_url = reverse_lazy('planner:recipe_list')

    # Add your context data
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(RecipeUpdate, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['form_type'] = 'Update'
        return context
    
    def post(self, request, *args, **kwargs):
        update_record = 0

        # Current Record
        recipe = get_object_or_404(self.model, id=self.kwargs['pk'])
        print("==============",recipe,"==============")
        # Form to hold the record with changes to update
        obj_form = RecipeForm(request.POST)
        obj_form = obj_form.save(commit = False)

        # Get the record with form data
        queryset = Recipe.objects.filter(user=self.request.user, day_of_the_week=obj_form.day_of_the_week, meal_type=obj_form.meal_type)

        # Check weather the record exists are not with form data
        if queryset.exists():
            # Check if the record exists is same as current the record that was updating
            if(recipe.id == queryset[0].id):
                update_record = 1
            else:
                messages.warning(request, "Selected 'Day' and 'Time' are already available. We had retrieved the record that you require, please update the record with required changes.")
                return redirect(reverse_lazy('planner:recipe_update', kwargs={'pk' : queryset[0].id}))
        else:
            update_record = 1

        if update_record == 1:
            form = RecipeForm(request.POST, instance=recipe)
            if not form.is_valid():
                context = {
                    'form':form
                }
                return render(request, self.template_name, context)
            form.save()
            messages.success(request, "You recipe is updated successfully.")
        
        return redirect(self.success_url)
    
# Delete Recipe
class RecipeDelete(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = 'planner/recipe_confirm_delete.html'
    success_url = reverse_lazy('planner:recipe_list')    
    http_method_names = ['get', 'post']
    pk_url_kwarg = 'pk'
    context_object_name = 'recipe'
    
    # Delete Recipe
    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(self.model, id=self.kwargs['pk'])
        if recipe.user == self.request.user:
            recipe.delete()
            messages.success(request, "Your recipe has been deleted successfully.")
        else:
            messages.error(request, "Your are not an author of the recipe.")
        return redirect(self.success_url)
    
# Admin View
class AdminView(LoginRequiredMixin, ListView):
    model = User
    http_method_names = ['get']
    context_object_name = 'user_list'
    template_name = 'planner/user_list.html'

    def get_queryset(self, *args, **kwargs):
        queryset = self.model.objects.filter(is_superuser=False)
        return queryset

# User Recipes
class UserRecipeView(LoginRequiredMixin, ListView):
    model = Recipe
    pk_url_kwarg = 'pk'
    template_name = 'planner/user_recipe_list.html'
    context_object_name = 'recipe_list'
    
    def get_queryset(self, *args, **kwargs):
        # Filter by logged in user and order by day_of_the_week and meal_type
        queryset = self.model.objects.filter(user=self.kwargs['pk']).order_by('day_of_the_week', 'meal_type')
        return queryset

# Update User Profile
class UserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'planner/user_form.html'
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('planner:recipe_list')
    success_message = "Your profile was updated successfully."

# Redirecting the users based on their role
def login_success(request):
    if request.user.is_superuser:
        return redirect('planner:admin_view')
    else:
        return redirect('planner:recipe_list')