from pydantic import TypeAdapter, HttpUrl, ValidationError


def validate_url(url: str) -> HttpUrl | None:
    url_adapter = TypeAdapter(HttpUrl)

    try:
        url_valid: HttpUrl = url_adapter.validate_python(url)
    except ValidationError:
        return None

    return url_valid


def url_to_filename(url: HttpUrl) -> str:
    filename = ""

    assert url.host or url.path, "Url must have one of: host, path"

    if url.host is not None:
        filename += url.host

    if url.path is not None:
        filename += url.path

    return filename.strip("/").replace("/", "-").replace(".", "_")

