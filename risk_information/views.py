from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
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


class RiskInformationRetrieveView(RetrieveUpdateAPIView):
    queryset = RiskInformation.objects.all().select_related(
        "risk_category",
        "country",
    )
    serializer_class = RiskInformationSerializer

    # GET is public (same as list), PUT/PATCH require auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # multipart to replace the upload file; JSON for metadata-only PATCH
    parser_classes = (MultiPartParser, FormParser, JSONParser)
