from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import HazardInformation
from .serializers import HazardInformationSerializer


class HazardInformationListView(ListCreateAPIView):
    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = HazardInformation.objects.all().order_by("-id")
    serializer_class = HazardInformationSerializer


class HazardInformationRetrieveView(RetrieveUpdateAPIView):
    # GET is public, PUT/PATCH require auth
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = HazardInformationSerializer
    queryset = HazardInformation.objects.all().select_related(
        "country",
        "hazard_type",
    )
