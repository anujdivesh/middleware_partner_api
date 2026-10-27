from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from .models import Event
from .serializers import EventSerializer


class EventPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200


class EventListCreateView(ListCreateAPIView):
    queryset = (
        Event.objects.all()
        .select_related("event_type", "country")
        .prefetch_related("citizen_sciences", "model_runs")
        .order_by("-id")
    )
    serializer_class = EventSerializer
    pagination_class = EventPagination

    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        country = self.request.query_params.get("country")
        if country:
            if not country.isdigit():
                raise ValidationError({"country": "Must be an integer country id."})
            queryset = queryset.filter(country_id=int(country))
        return queryset


class EventByCountryListView(ListAPIView):
    serializer_class = EventSerializer
    pagination_class = EventPagination
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return (
            Event.objects.filter(country_id=self.kwargs["country_id"])
            .select_related("event_type", "country")
            .prefetch_related("citizen_sciences", "model_runs")
            .order_by("-id")
        )


class EventRetrieveView(RetrieveUpdateAPIView):
    queryset = (
        Event.objects.all()
        .select_related("event_type", "country")
        .prefetch_related("citizen_sciences", "model_runs")
    )
    serializer_class = EventSerializer

    # GET is public (same as list), PUT/PATCH require auth
    permission_classes = (IsAuthenticatedOrReadOnly,)
