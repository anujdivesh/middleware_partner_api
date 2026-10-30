"""
URL configuration for middleware_partner_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import docs, views

from .admin_site import partner_admin_site


admin.site.site_header = "PaRTnR2 API"
admin.site.site_title = "PaRTnR2 API"
admin.site.index_title = "PaRTnR2 API"

from country.views import CountryListView, CountryRetrieveView
from django.urls import include
from cyclone_track.views import (
    CycloneTrackLatestView,
    CycloneTrackListCreateView,
    CycloneTrackRetrieveView,
)
from risk_information.views import RiskInformationListCreateView, RiskInformationRetrieveView
from hazard_information.views import HazardInformationListView, HazardInformationRetrieveView
from citizen_science.views import CitizenScienceListCreateView
from event.views import (
    EventByCountryListView,
    EventByTypeListView,
    EventListCreateView,
    EventRetrieveView,
)
from event_type.views import EventTypeListView, EventTypeRetrieveView
from model.views import ModelListView, ModelRetrieveView, ModelRunListView, ModelRunRetrieveView
from model.views_update import ModelRunUpdateCompletedView
from model.views_logs import ModelLogsListCreateView
from mailer.views import (
    MailConfigurationDetailView,
    MailConfigurationListCreateView,
    MailConfigurationSendView,
    MailRecipientDetailView,
    MailRecipientListCreateView,
    SendEmailView,
)



urlpatterns = [
    path("", views.root),
    path("partner_api/", views.partner_api_root),
    path("partner_api/admin/", partner_admin_site.urls),
    path("partner_api/api-token-auth/", views.ObtainExpiringAuthToken.as_view()),

    # API docs
    path("partner_api/docs/", docs.api_docs, name="api-docs"),
    path("partner_api/redoc/", RedirectView.as_view(pattern_name="api-docs")),
    path("partner_api/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="api-swagger"),
    path("partner_api/schema/", SpectacularAPIView.as_view(), name="schema"),

    path("partner_api/v1/country/", CountryListView.as_view()),
    path("partner_api/v1/country/<int:pk>", CountryRetrieveView.as_view()),
    path("partner_api/v1/country/<int:pk>/", CountryRetrieveView.as_view()),
    path("partner_api/v1/cyclone_track/", CycloneTrackListCreateView.as_view()),
    path("partner_api/v1/cyclone_track/<int:pk>", CycloneTrackRetrieveView.as_view()),
    path("partner_api/v1/cyclone_track/<int:pk>/", CycloneTrackRetrieveView.as_view()),
    path("partner_api/v1/cyclone_track/latest", CycloneTrackLatestView.as_view()),
    path("partner_api/v1/cyclone_track/latest/", CycloneTrackLatestView.as_view()),
    path("partner_api/v1/risk_information/", RiskInformationListCreateView.as_view()),
    path("partner_api/v1/risk_information/<int:pk>", RiskInformationRetrieveView.as_view()),
    path("partner_api/v1/risk_information/<int:pk>/", RiskInformationRetrieveView.as_view()),
    path("partner_api/v1/hazard_information/", HazardInformationListView.as_view()),
    path(
        "partner_api/v1/hazard_information/<int:pk>",
        HazardInformationRetrieveView.as_view(),
    ),
    path(
        "partner_api/v1/hazard_information/<int:pk>/",
        HazardInformationRetrieveView.as_view(),
    ),
    path("partner_api/v1/citizen_science/", CitizenScienceListCreateView.as_view()),
    path("partner_api/v1/event/", EventListCreateView.as_view()),
    path("partner_api/v1/event/<int:pk>", EventRetrieveView.as_view()),
    path("partner_api/v1/event/<int:pk>/", EventRetrieveView.as_view()),
    path("partner_api/v1/event/country/<int:country_id>", EventByCountryListView.as_view()),
    path("partner_api/v1/event/country/<int:country_id>/", EventByCountryListView.as_view()),
    path("partner_api/v1/event/event_type/<int:event_type_id>", EventByTypeListView.as_view()),
    path("partner_api/v1/event/event_type/<int:event_type_id>/", EventByTypeListView.as_view()),
    path("partner_api/v1/event_type/", EventTypeListView.as_view()),
    path("partner_api/v1/event_type/<int:pk>", EventTypeRetrieveView.as_view()),
    path("partner_api/v1/event_type/<int:pk>/", EventTypeRetrieveView.as_view()),

    # Model
    path("partner_api/v1/model/", ModelListView.as_view()),
    path("partner_api/v1/model/<int:pk>", ModelRetrieveView.as_view()),
    path("partner_api/v1/model/<int:pk>/", ModelRetrieveView.as_view()),

    # ModelRun
    path("partner_api/v1/model_run/", ModelRunListView.as_view()),
    path("partner_api/v1/model_run/<int:pk>", ModelRunRetrieveView.as_view()),
    path("partner_api/v1/model_run/<int:pk>/", ModelRunRetrieveView.as_view()),
        # PATCH model_run_completed
        path("partner_api/v1/model_run/<int:pk>/update_completed/", ModelRunUpdateCompletedView.as_view()),

        # ModelLogs
        path("partner_api/v1/model_run_logs/", ModelLogsListCreateView.as_view()),

    # Mailer
    path("partner_api/v1/mailer/send/", SendEmailView.as_view()),
    path("partner_api/v1/mailer/recipients/", MailRecipientListCreateView.as_view()),
    path("partner_api/v1/mailer/recipients/<int:pk>/", MailRecipientDetailView.as_view()),
    path("partner_api/v1/mailer/configurations/", MailConfigurationListCreateView.as_view()),
    path("partner_api/v1/mailer/configurations/<int:pk>/", MailConfigurationDetailView.as_view()),
    path("partner_api/v1/mailer/configurations/<int:pk>/send/", MailConfigurationSendView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
