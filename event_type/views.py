from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import EventType
from .serializers import EventTypeSerializer


class EventTypeListView(ListAPIView):
    queryset = EventType.objects.all().order_by("id")
    serializer_class = EventTypeSerializer
    permission_classes = (AllowAny,)


class EventTypeRetrieveView(RetrieveAPIView):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    permission_classes = (AllowAny,)
