from django.core.management.base import BaseCommand, CommandError
from Parking.models import *
from shapely.geometry import Polygon 
import random
import math
import time
import string

def generate_parking():
    radius = 350
    offset_x = 950
    offset_y = 350
    random_coords = []
    entrance_width = 0.5
    start_angle = random.random() * math.pi * 2
    angle = start_angle
    while angle < start_angle + math.pi * 2 - entrance_width:
        random_coords.append([offset_x + radius * math.cos(angle), offset_y + radius * math.sin(angle)])
        angle += 2 - random.random() * 1.5
    random_coords.append([offset_x + radius * math.cos(start_angle - entrance_width), offset_y + radius * math.sin(start_angle - entrance_width)])

    parking = Parking(name=f"Parking ul. Testowa {random.randint(0,1000)}")
    parking.save()
    for x, y in random_coords:
        coords = Coordinates(x=x, y=y)
        coords.save()
        parking.coords.add(coords)
    print(f"Parking id-{parking.id} generated")
    return parking.id

def check_intersection(spot, spots):
    spot_polygon = Polygon(spot)
    for s in spots:
        other_polygon = Polygon(s)
        if spot_polygon.intersects(other_polygon):
            return True
    return False

def check_parking_location(spot, parking):
    spot_polygon = Polygon(spot)
    parking_polygon = Polygon(parking).reverse()

    if spot_polygon.within(parking_polygon):
        #print(spot_polygon.intersection(parking_polygon).area)
        return True
    return False

def move_on_line(point1: list[float], point2: list[float], distance: float) -> list[float] | None:
    points_dx = point2[0] - point1[0]
    points_dy = point2[1] - point1[1]
    points_distance = ((points_dx)**2 + (points_dy)**2)**.5
    

    if distance > points_distance or points_distance == 0:
        return None
    
    distance_r = distance / points_distance
    dx = points_dx * distance_r
    dy = points_dy * distance_r

    return [point1[0] + dx, point1[1] + dy]

def move_perpendicularly(point1, point2, distance, inside=True) -> list[float] | None:
    points_dx = point2[0] - point1[0]
    points_dy = point2[1] - point1[1]
    points_distance = ((points_dx) ** 2 + (points_dy) ** 2) ** 0.5
    
    if points_distance == 0:
        return None
    
    perpendicular_dx = -points_dy / points_distance
    perpendicular_dy = points_dx / points_distance
    if not inside:
        perpendicular_dx, perpendicular_dy = -perpendicular_dx, -perpendicular_dy

    new_point = [point1[0] + perpendicular_dx * distance, point1[1] + perpendicular_dy * distance]
    
    return new_point

def generate_parking_slots(parking_id):
    parking = Parking.objects.get(id=parking_id)

    # Parking slot params
    car_width = 60
    car_length = 135
    car_margin = 25

    parking_coords = parking.coords_list
    parking_slots = []
    for i, c in enumerate(parking_coords[:-1]):
        print(i)
        corner1 = move_on_line(c, parking_coords[i+1], car_margin)
        while corner1 is not None:
            corner2 = move_on_line(corner1, parking_coords[i+1], car_width)

            if corner2 is None:
                break

            corner3 = move_perpendicularly(corner2, parking_coords[i+1], car_length)
            corner4 = move_perpendicularly(corner1, parking_coords[i+1], car_length)
            
            new_parking_slot = [corner1, corner2, corner3, corner4]
            if not check_intersection(new_parking_slot, parking_slots): # and check_parking_location(new_parking_slot, parking_coords):
                parking_slots.append(new_parking_slot)
                corner1 = move_on_line(corner2, parking_coords[i+1], car_margin)
            else:
                corner1 = move_on_line(corner1, parking_coords[i+1], car_margin)

    parking_slot_char = random.choice(string.ascii_uppercase[:8])
    for i, ps in enumerate(parking_slots):
        parking_slot = ParkingSlot(name=f"{parking_slot_char}{f'{i+1}'.rjust(3, '0')}", parking=parking)
        parking_slot.save()
        for x, y in ps:
            coords = Coordinates(x=x, y=y)
            coords.save()
            parking_slot.coords.add(coords)
    print("Parking slots generated")

class Command(BaseCommand):
    help = "Generates random Parking, ParkingSlot and Coordinates objects"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        parking_id = generate_parking()
        generate_parking_slots(parking_id)