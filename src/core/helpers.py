from pydantic import TypeAdapter, HttpUrl, ValidationError


def validate_url(url: str) -> HttpUrl | None:
    url_adapter = TypeAdapter(HttpUrl)

    try:
        url_valid: HttpUrl = url_adapter.validate_python(url)
    except ValidationError:
        return None

    return url_valid


def url_to_filename(url: HttpUrl) -> str:
    return (url.host + url.path).strip("/").replace("/", "-").replace(".", "_")

