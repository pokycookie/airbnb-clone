from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django_countries import countries
from . import models, forms


class HomeView(ListView):

    """HomeView Definition"""

    model = models.Room
    paginate_by = 10
    paginate_orphans = 5
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context


class RoomDetail(DetailView):

    """ RoomDetail Definition """

    model = models.Room


def search(request):

    city = request.GET.get("city", "Anywhere")
    city = str.capitalize(city)
    room_type = int(request.GET.get("room_type", 0))
    country = request.GET.get("country", "0")
    price = int(request.GET.get("price", 0))
    guests = int(request.GET.get("guests", 0))
    bedrooms = int(request.GET.get("bedrooms", 0))
    beds = int(request.GET.get("beds", 0))
    bathrooms = int(request.GET.get("bathrooms", 0))
    instant = bool(request.GET.get("instant", False))
    super_host = bool(request.GET.get("super_host", False))
    s_amenities = request.GET.getlist("amenity")
    s_facilities = request.GET.getlist("facility")

    form = {
        "s_city": city,
        "s_room_type": room_type,
        "s_country": country,
        "s_price": price,
        "s_guests": guests,
        "s_bedrooms": bedrooms,
        "s_beds": beds,
        "s_bathrooms": bathrooms,
        "s_amenities": s_amenities,
        "s_facilities": s_facilities,
        "s_instant": instant,
        "s_super_host": super_host,
    }

    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()
    facilities = models.Facility.objects.all()

    choices = {
        "countries": countries,
        "room_types": room_types,
        "amenities": amenities,
        "facilities": facilities,
    }

    filter_args = {}

    if city != "Anywhere":
        filter_args["city__startswith"] = city

    if country != "0":
        filter_args["country"] = country

    if room_type != 0:
        filter_args["room_type__pk__exact"] = room_type

    if price != 0:
        filter_args["price__lte"] = price

    if guests != 0:
        filter_args["guest__gte"] = guests

    if bedrooms != 0:
        filter_args["bedrooms__gte"] = bedrooms

    if beds != 0:
        filter_args["beds__gte"] = beds

    if bathrooms != 0:
        filter_args["baths__gte"] = bathrooms

    if instant is True:
        filter_args["instant_book"] = True

    if super_host is True:
        filter_args["host__superhost"] = True

    if len(s_amenities) > 0:
        for a in s_amenities:
            filter_args["amenities__pk"] = int(a)

    if len(s_facilities) > 0:
        for f in s_facilities:
            filter_args["facilities__pk"] = int(f)

    rooms = models.Room.objects.filter(**filter_args)

    return render(request, "rooms/search.html", {**form, **choices, "rooms": rooms})
