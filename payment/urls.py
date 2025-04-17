from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('donate/', views.Donate.as_view(), name = 'donate'),
    path('handler/', views.handler, name = 'handler')
]