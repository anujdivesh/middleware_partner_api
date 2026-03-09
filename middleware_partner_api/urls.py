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
from . import views
from rest_framework.authtoken.views import obtain_auth_token


admin.site.site_header = "PaRTnR2 API"
admin.site.site_title = "PaRTnR2 API"
admin.site.index_title = "PaRTnR2 API"

from country.views import CountryListView
from django.urls import include
from cyclone_track.views import CycloneTrackListCreateView
from risk_information.views import RiskInformationListCreateView
from hazard_information.views import HazardInformationListView
from citizen_science.views import CitizenScienceListCreateView
from event.views import EventListCreateView



urlpatterns = [
    path("", views.root),
    path("partner_api/", views.partner_api_root),
    path("partner_api/admin/", admin.site.urls),
    path("partner_api/api-token-auth/", obtain_auth_token),
    path("partner_api/v1/country/", CountryListView.as_view()),
    path("partner_api/v1/cyclone_track/", CycloneTrackListCreateView.as_view()),
    path("partner_api/v1/risk_information/", RiskInformationListCreateView.as_view()),
    path("partner_api/v1/hazard_information/", HazardInformationListView.as_view()),
    path("partner_api/v1/citizen_science/", CitizenScienceListCreateView.as_view()),
    path("partner_api/v1/event/", EventListCreateView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
