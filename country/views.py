from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Country
from .serializers import CountrySerializer

class CountryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(operation_id="country_list", responses=CountrySerializer(many=True))
    def get(self, request):
        countries = Country.objects.all().prefetch_related("islands", "regions")
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)


class CountryRetrieveView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CountrySerializer

    def get_queryset(self):
        return Country.objects.all().prefetch_related("islands", "regions")
