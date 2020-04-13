from django.core.management.base import BaseCommand
from rooms import models as room_models


class Command(BaseCommand):

    help = "Create Origin Amenities"

    def handle(self, *args, **options):
        amenities = [
            "Kitchen",
            "Shampoo",
            "Heating",
            "Air conditioning",
            "Washer",
            "Dryer",
            "Wifi",
            "Breakfast",
            "Indoor fireplace",
            "Hangers",
            "Iron",
            "Hair dryer",
            "Laptop-friendly workspace",
            "TV",
            "Crib",
            "High chair",
            "Self check-in",
            "Smoke alarm",
            "Carbon monoxide alarm",
            "Private bathroom",
            "Beachfront",
            "Waterfront",
            "Ski-in/ski-out",
        ]
        for i in amenities:
            room_models.Amenity.objects.create(name=i)
        self.stdout.write(self.style.SUCCESS("Amenities created!"))
