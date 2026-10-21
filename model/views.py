from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from .models import Model, ModelRun
from .serializers import ModelRunSerializer, ModelSerializer

@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "model_run_completed",
                OpenApiTypes.BOOL,
                description="Filter by completion (true/false).",
            )
        ]
    )
)
class ModelRunListView(ListCreateAPIView):
    serializer_class = ModelRunSerializer

    def get_queryset(self):
        queryset = ModelRun.objects.all().order_by('-id')
        model_run_completed = self.request.query_params.get('model_run_completed')
        if model_run_completed is not None:
            if model_run_completed.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(model_run_completed=True)
            elif model_run_completed.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(model_run_completed=False)
        return queryset

class ModelRunRetrieveView(RetrieveUpdateAPIView):
    queryset = ModelRun.objects.all()
    serializer_class = ModelRunSerializer

class ModelListView(ListCreateAPIView):
    queryset = Model.objects.all().order_by('id')
    serializer_class = ModelSerializer

class ModelRetrieveView(RetrieveUpdateAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
