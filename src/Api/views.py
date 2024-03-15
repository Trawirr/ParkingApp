from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Parking.models import *

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'It\'s a test paragraph'})

@api_view(['GET'])
def parking_coords(request):
    return Response({'coords': [Parking.objects.all()[Parking.objects.all().count()-1].coords_list]})

@api_view(['GET'])
def parking_slots_coords(request):
    return Response({'coords': Parking.objects.all()[Parking.objects.all().count()-1].slots_coords_list})