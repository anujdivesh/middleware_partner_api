from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Country
from .serializers import CountrySerializer

class CountryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        countries = Country.objects.all().prefetch_related("islands")
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)
