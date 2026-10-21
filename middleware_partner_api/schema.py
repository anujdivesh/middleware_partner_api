"""OpenAPI schema helpers for drf-spectacular (docs at /partner_api/docs/)."""

API_DESCRIPTION = """
REST API for the Pacific Disaster / PaRTnR2 partner platform.

## Authentication

1. Get a token with `POST /partner_api/api-token-auth/` (form or JSON body with
   `username` and `password`). The response contains `token` and `expires_at`.
   Tokens expire **2 days** after they are issued; request a new one after that.
2. Send it on every request: `Authorization: Token <token>`.

In this page, click **Authorize**, choose `tokenAuth` and enter `Token <token>`
(including the word `Token`).

## Access rules

| Resource | Read (GET) | Write (POST / PUT / PATCH) |
|---|---|---|
| Events, hazard information, risk information | public | token required |
| Models, model runs, model run logs | token required | token required |
| Mailer configurations / recipients | admin only | admin only |

`PUT` replaces the whole record (all required fields); `PATCH` updates only the
fields you send.

## Notes

- Related records (country, event type, model runs, ...) are referenced by id.
- Event, risk information lists are paginated: `?page=2&page_size=50` (max 200).
- Risk information `upload` is a file (`.geojson`, `.csv`, `.gpkg`), so create and
  replace it with `multipart/form-data`.
"""


def drop_duplicate_and_admin_paths(endpoints):
    """Hide the admin and the no-trailing-slash aliases of the same endpoints."""
    return [
        (path, path_regex, method, callback)
        for path, path_regex, method, callback in endpoints
        if path.endswith("/") and "/admin/" not in path
    ]
