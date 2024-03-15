from django.urls import path
from . import views

urlpatterns = [
    path('hello-world/', views.hello_world, name='hello_world'),
    path('parking_coords/', views.parking_coords, name='parking_coords'),
    path('parking_slots_coords/', views.parking_slots_coords, name='parking_slots_coords'),
]