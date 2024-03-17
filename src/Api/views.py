from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from Parking.models import *

@api_view(['GET'])
def hello_world(request):
    return Response({'message': 'It\'s a test paragraph'})

@api_view(['GET'])
def parking_coords(request, parking_id: int):
    parking = Parking.objects.get(id=parking_id)
    return Response({'coords': [parking.coords_list]})

@api_view(['GET'])
def parking_slots_coords(request, parking_id: int):
    parking = Parking.objects.get(id=parking_id)
    print(parking.slots_data)
    return Response(parking.slots_data)