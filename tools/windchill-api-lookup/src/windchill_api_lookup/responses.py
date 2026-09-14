"""The same JSON envelope is used by command-line and MCP transports."""

from collections.abc import Callable

from windchill_api_lookup.errors import ApiLookupError


def success(payload: dict) -> dict:
    return {"ok": True, **payload}


def failure(error: ApiLookupError) -> dict:
    return {"ok": False, "error": {
        "code": error.code, "message": str(error), "details": error.details,
    }}


def query_response(operation: Callable[[], dict]) -> dict:
    try:
        return success(operation())
    except ApiLookupError as exc:
        return failure(exc)
    except OSError as exc:
        return failure(ApiLookupError("INDEX_UNAVAILABLE", str(exc)))
