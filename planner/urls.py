from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.IndexView.as_view(), name = 'index_view'),
    path('recipes/', views.RecipeList.as_view(), name='recipe_list'),
    path('create/', views.RecipeCreate.as_view(), name='recipe_create'),
    path('recipes/pdf', views.RecipeListPdf.as_view(), name='recipe_list_pdf'),
    path('recipes/<int:pk>/update/', views.RecipeUpdate.as_view(), name='recipe_update'),
    path('recipes/<int:pk>/delete/', views.RecipeDelete.as_view(), name='recipe_delete'),
    path('users/', views.AdminView.as_view(), name='admin_view'),
    path('user/recipes/<int:pk>/', views.UserRecipeView.as_view(), name='user_recipe_view'),
    path('user/profile/<int:pk>/', views.UserProfileView.as_view(), name='user_update'),
]