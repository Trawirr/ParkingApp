from django.db import models


class Coordinates(models.Model):
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Coords {self.id}. ({self.x}, {self.y})"

class Parking(models.Model):
    name = models.CharField(max_length=50)
    coords = models.ManyToManyField(Coordinates, related_name='parking')

    @property
    def coords_list(self):
        return [[c.x, c.y] for c in self.coords.all()]
    
    @property
    def slots_coords_list(self) -> list:
        return [[[c.x, c.y] for c in ps.coords.all()] for ps in self.slots.all()]
    
    @property
    def slots_data(self) -> dict:
        data = {'coords': [], 'occupancy': []}
        for ps in self.slots.all():
            data['coords'].append([[c.x, c.y] for c in ps.coords.all()])
            data['occupancy'].append(ps.is_occupied)
        return data

class ParkingSlot(models.Model):
    name = models.CharField(max_length=50)
    coords = models.ManyToManyField(Coordinates, related_name='slot')
    parking = models.ForeignKey(Parking, on_delete=models.CASCADE, related_name='slots')
    is_occupied = models.BooleanField(default=False)