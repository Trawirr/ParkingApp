from django.contrib import admin
from .models import *

class CoordinatesPInLine(admin.TabularInline):
    model = Parking.coords.through

class CoordinatesSInLine(admin.TabularInline):
    model = ParkingSlot.coords.through

@admin.register(Coordinates)
class CoordinatesParkingAdmin(admin.ModelAdmin):
    inlines = [
        CoordinatesPInLine,
        CoordinatesSInLine
    ]
    list_display = ('id', 'x', 'y')
    ordering = ('id', )

class ParkingSlotInLine(admin.TabularInline):
    model = ParkingSlot

@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    inlines = [
        CoordinatesSInLine
    ]
    list_display = ('name', 'parking')

@admin.register(Parking)
class ParkingAdmin(admin.ModelAdmin):
    inlines = [
        ParkingSlotInLine,
        CoordinatesPInLine
    ]
    list_display = ('name', )