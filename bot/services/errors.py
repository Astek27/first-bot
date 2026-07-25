class ExternalServiceError(Exception):
    """Raised when Yandex Maps / Geocoder / Overpass lookup fails after retries."""
