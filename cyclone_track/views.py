from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import CycloneTrack
from .serializers import CycloneTrackSerializer


class CycloneTrackListCreateView(ListCreateAPIView):
    queryset = CycloneTrack.objects.all().order_by("-id")
    serializer_class = CycloneTrackSerializer

    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # Needed for file upload
    parser_classes = (MultiPartParser, FormParser)
