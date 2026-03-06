from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import HazardInformation
from .serializers import HazardInformationSerializer


class HazardInformationListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = HazardInformation.objects.all().order_by("-id")
    serializer_class = HazardInformationSerializer
