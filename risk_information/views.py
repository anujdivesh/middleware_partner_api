from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import RiskInformation
from .serializers import RiskInformationSerializer


class RiskInformationPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200


class RiskInformationListCreateView(ListCreateAPIView):
    queryset = RiskInformation.objects.all().order_by("-id")
    serializer_class = RiskInformationSerializer
    pagination_class = RiskInformationPagination

    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # Needed for file upload
    parser_classes = (MultiPartParser, FormParser)
