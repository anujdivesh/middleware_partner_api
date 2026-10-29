from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from middleware_partner_api.filters import filter_date_range
from .models import Model, ModelRun
from .serializers import ModelRunSerializer, ModelSerializer

@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "model_run_completed",
                OpenApiTypes.BOOL,
                description="Filter by completion (true/false).",
            ),
            OpenApiParameter(
                "start_date",
                OpenApiTypes.STR,
                description="Runs with model_run_time on/after this (YYYY-MM-DD or ISO 8601).",
            ),
            OpenApiParameter(
                "end_date",
                OpenApiTypes.STR,
                description="Runs with model_run_time on/before this (YYYY-MM-DD covers the whole day).",
            ),
        ]
    )
)
class ModelRunListView(ListCreateAPIView):
    serializer_class = ModelRunSerializer

    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = ModelRun.objects.all().order_by(
            F('model_run_time').desc(nulls_last=True), '-id'
        )
        model_run_completed = self.request.query_params.get('model_run_completed')
        if model_run_completed is not None:
            if model_run_completed.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(model_run_completed=True)
            elif model_run_completed.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(model_run_completed=False)
        return filter_date_range(queryset, self.request.query_params, 'model_run_time')

class ModelRunRetrieveView(RetrieveUpdateAPIView):
    queryset = ModelRun.objects.all()
    serializer_class = ModelRunSerializer

    # GET is public, PUT/PATCH require auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

class ModelListView(ListCreateAPIView):
    queryset = Model.objects.all().order_by('id')
    serializer_class = ModelSerializer

    # GET is public, POST requires auth
    permission_classes = (IsAuthenticatedOrReadOnly,)

class ModelRetrieveView(RetrieveUpdateAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer

    # GET is public, PUT/PATCH require auth
    permission_classes = (IsAuthenticatedOrReadOnly,)
