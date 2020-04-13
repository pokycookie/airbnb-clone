import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django_seed import Seed
from reservations import models as reservation_models
from rooms import models as room_models
from users import models as user_models


class Command(BaseCommand):

    help = "Create Reservations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            default=1,
            type=int,
            help="How many reservations you want to create",
        )

    def handle(self, *args, **options):
        number = options.get("number")
        seeder = Seed.seeder()
        rooms = room_models.Room.objects.all()
        guest = user_models.User.objects.all()
        seeder.add_entity(
            reservation_models.Reservation,
            number,
            {
                "status": lambda x: random.choice(["pending", "confirmed", "canceled"]),
                "guest": lambda x: random.choice(guest),
                "room": lambda x: random.choice(rooms),
                "check_in": lambda x: datetime.now()
                + timedelta(days=random.randint(-10, 0)),
                "check_out": lambda x: datetime.now()
                + timedelta(days=random.randint(1, 10)),
            },
        )
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"{number} Reservations created!"))
