"""Simple, human-readable API docs page at /partner_api/docs/.

Endpoints are listed here; fields are read from the serializers so they stay in
sync with the code. The full interactive reference is at /partner_api/swagger/.
"""

import json

from django.shortcuts import render
from rest_framework import serializers

from cyclone_track.serializers import CycloneTrackSerializer
from event.serializers import EventSerializer
from hazard_information.serializers import HazardInformationSerializer
from model.serializers import ModelRunSerializer, ModelSerializer
from risk_information.serializers import RiskInformationSerializer

PUBLIC_READ = "GET is public · POST/PUT/PATCH need a token"
TOKEN_ALL = "Token needed for everything"

# (method, url suffix, description); resources list the ones they support.
CALLS = {
    "list": ("GET", "", "List records"),
    "get": ("GET", "{id}/", "Get one record"),
    "create": ("POST", "", "Create a record"),
    "replace": ("PUT", "{id}/", "Replace a record (send all required fields)"),
    "update": ("PATCH", "{id}/", "Change only the fields you send"),
}
ALL_CALLS = list(CALLS)

RESOURCES = [
    {
        "slug": "events",
        "title": "Events",
        "path": "/partner_api/v1/event/",
        "summary": "A disaster event, linked to one or more model runs.",
        "access": PUBLIC_READ,
        "serializer": EventSerializer,
    },
    {
        "slug": "hazards",
        "title": "Hazard information",
        "path": "/partner_api/v1/hazard_information/",
        "summary": "Hazard map layers (WMS/WFS/etc. links).",
        "access": PUBLIC_READ,
        "serializer": HazardInformationSerializer,
    },
    {
        "slug": "risks",
        "title": "Risk information",
        "path": "/partner_api/v1/risk_information/",
        "summary": "Risk/impact data uploaded as .geojson, .csv or .gpkg.",
        "access": PUBLIC_READ,
        "serializer": RiskInformationSerializer,
        "multipart": True,
        "note": "Send as form data (multipart), because it includes a file upload. "
        "To change only text fields, PATCH with JSON is fine.",
    },
    {
        "slug": "cyclone-tracks",
        "title": "Cyclone tracks",
        "path": "/partner_api/v1/cyclone_track/",
        "summary": "Cyclone track forecasts uploaded as a CSV file; the track geometry is built from the file.",
        "access": "GET is public · POST needs a token",
        "serializer": CycloneTrackSerializer,
        "calls": ["list", "get", "create"],
        "multipart": True,
        "sample_file": "track.csv",
        "note": "The list is newest first (by issued_time). Filter it with ?cyclone_track_type=, "
        "?country=, ?start_date= and ?end_date=. GET /partner_api/v1/cyclone_track/latest/ "
        "returns the single latest track and takes the same filters. "
        "Send as form data (multipart) with the CSV in track_file. cyclone_name is "
        "filled from the CSV if you leave it out. Set notify=true together with a "
        "mail_configuration id to email that configuration's recipients after upload.",
    },
    {
        "slug": "model-runs",
        "title": "Model runs",
        "path": "/partner_api/v1/model_run/",
        "summary": "One run of one or more models, with its hazards and risks.",
        "access": PUBLIC_READ,
        "serializer": ModelRunSerializer,
        "note": "The list is newest first (by model_run_time). Filter it with "
        "?model_run_completed=true or false, and/or ?start_date= and ?end_date= "
        "(YYYY-MM-DD or ISO 8601, both inclusive). "
        "To only mark a run complete: PATCH /partner_api/v1/model_run/{id}/update_completed/ "
        'with {"model_run_completed": true}.',
    },
    {
        "slug": "models",
        "title": "Models",
        "path": "/partner_api/v1/model/",
        "summary": "The models that can be run.",
        "access": PUBLIC_READ,
        "serializer": ModelSerializer,
    },
]


def _related_name(field) -> str:
    queryset = getattr(field, "queryset", None)
    return queryset.model._meta.verbose_name if queryset is not None else ""


def _describe(field):
    """(type label, example value) for a serializer field."""
    if isinstance(field, serializers.ManyRelatedField):
        name = _related_name(field.child_relation)
        return f"list of {name} ids", [1]
    if isinstance(field, serializers.PrimaryKeyRelatedField):
        return f"{_related_name(field)} id", 1
    if isinstance(field, serializers.FileField):
        return "file", None
    if isinstance(field, serializers.BooleanField):
        return "true / false", False
    if isinstance(field, serializers.DateTimeField):
        return "date-time", "2026-01-31T09:00:00Z"
    if isinstance(field, serializers.URLField):
        return "URL", "https://example.org/wms"
    if isinstance(field, serializers.EmailField):
        return "email", "someone@spc.int"
    if isinstance(field, (serializers.IntegerField, serializers.FloatField)):
        return "number", 0
    if isinstance(field, serializers.JSONField):
        return "JSON", {}
    return "text", "text"


def _fields(serializer_class):
    rows, example, files = [], {}, []
    for name, field in serializer_class().fields.items():
        type_label, value = _describe(field)
        rows.append(
            {
                "name": name,
                "type": type_label,
                "required": field.required and not field.read_only,
                "read_only": field.read_only,
            }
        )
        if field.read_only:
            continue
        if value is None:
            files.append(name)
        else:
            example[name] = value
    return rows, example, files


def _curl_create(resource, base_url, example, files):
    url = base_url + resource["path"]
    if resource.get("multipart"):
        parts = [
            f"-F '{k}={json.dumps(v) if isinstance(v, bool) else v}'"
            for k, v in example.items()
            if not isinstance(v, (list, dict))
        ]
        parts += [f"-F '{name}=@{resource.get('sample_file', 'my_file.geojson')}'" for name in files]
        body = " \\\n  ".join(parts)
        return f'curl -X POST {url} \\\n  -H "Authorization: Token YOUR_TOKEN" \\\n  {body}'
    return (
        f"curl -X POST {url} \\\n"
        '  -H "Authorization: Token YOUR_TOKEN" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        f"  -d '{json.dumps(example)}'"
    )


def api_docs(request):
    base_url = request.build_absolute_uri("/").rstrip("/")
    resources = []
    for resource in RESOURCES:
        rows, example, files = _fields(resource["serializer"])
        call_keys = resource.get("calls", ALL_CALLS)
        resources.append(
            {
                **resource,
                "calls": [CALLS[key] for key in call_keys],
                "can_update": "update" in call_keys,
                "read_needs_token": resource["access"] == TOKEN_ALL,
                "fields": rows,
                "curl_create": _curl_create(resource, base_url, example, files),
            }
        )

    email_example = {
        "recipients": ["someone@spc.int"],
        "subject": "Test",
        "message": "Hello from the API",
    }
    return render(
        request,
        "api_docs.html",
        {
            "base_url": base_url,
            "resources": resources,
            "email_example": json.dumps(email_example),
        },
    )
