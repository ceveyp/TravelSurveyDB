import requests

from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)


class AddressValidator:
    def __init__(self):
        self._validation_endpoint_uri = "https://addressvalidation.googleapis.com/v1:validateAddress"
        self._geocode_endpoint_uri = "https://maps.googleapis.com/maps/api/geocode/json"
        self._config = get_config()

    def geocode(self, address_line: str):
        logger.debug(f"Geocode address: {address_line}")
        params = {
            "address": address_line,
            "key": self._config.google_api_key
        }
        resp = requests.get(self._geocode_endpoint_uri, params=params, timeout=5)
        if not resp.ok:
            raise RuntimeError(f"Geocode API error: {resp.text}")
        data = resp.json()
        if data["status"] != "OK":
            raise ValueError(f"Geocoding failed for address: {address_line}")
        place_id = data["results"][0]["place_id"]
        logger.debug(f"Geocode completed: {place_id}")
        return place_id

    def validate(self, address_line: str) -> str:
        try:
            logger.debug(f"Validating address line: {address_line}")
            payload = {"address": {"addressLines": [address_line]}}
            params = {"key": self._config.google_api_key}
            resp = requests.post(self._validation_endpoint_uri, json=payload, params=params, timeout=5)
            if not resp.ok:
                raise RuntimeError(f"Google Maps API error: {resp.text}")
            data = resp.json()
            verdict = data["result"]["verdict"]
            if not verdict["possibleNextAction"] == 'ACCEPT':
                raise ValueError(f"Address did not validate: {verdict}")
            logger.debug(f"Address validated: {address_line}")
            place_id = data["result"]["geocode"]["placeId"]
            logger.debug(f"Place ID: {place_id}")
            return place_id
        except Exception as e:
            logger.warning(e)
            logger.warning(f"Error validating address: {address_line}, trying Geocode API")
            return self.geocode(address_line)
