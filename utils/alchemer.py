from typing import Dict
from uuid import uuid4

import requests

from db.models.hotel import HotelContact
from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)


class Alchemer:
    def __init__(self):
        self._config = get_config()
        self._base_url = "https://api.alchemer.com/v5"
        self._auth_params = {
            "api_token": self._config.alchemer_api_key,
            "api_token_secret": self._config.alchemer_api_secret
        }

    def _api_call(self, method: str, uri: str, params: Dict | None = None) -> Dict:
        if not params:
            params = {}
        params.update(**self._auth_params)
        resp = requests.request(method=method, url=uri, params=params, timeout=5)
        if not resp.ok:
            raise RuntimeError(f"Alchemer API error: {resp.text}")
        data = resp.json()
        if not data.get('result_ok'):
            raise RuntimeError(f"Alchemer API error: {resp.text}")
        return data

    def get_contact_list_id(self):
        uri = f"{self._base_url}/contactlist"
        self._api_call('GET', uri)

    def create_contact_list(self, list_name: str | None = None) -> int:
        uri = f"{self._base_url}/contactlist"
        if not list_name:
            list_name = uuid4().hex
        params = {"list_name": list_name}
        data = self._api_call('PUT', uri, params)
        return data['data']['id']

    def create_contact(self, contact_list_id: int, contact: HotelContact):
        uri = f"{self._base_url}/contactlist/{contact_list_id}/contactlistcontact"
        params = {
            "email_address": contact.email,
            "status": "Active",
            "organization": contact.hotel.chain.name,
            "first_name": contact.name,
            "title": contact.title,
            "role": contact.role,
            "business_phone": contact.phone,
            "mailing_address": contact.hotel.address,
            "mailing_address_city": contact.hotel.city,
            "mailing_address_state": contact.hotel.state,
            "mailing_address_postal": contact.hotel.postal_code,
            "mailing_address_country": contact.hotel.country,
            "brandname": contact.hotel.chain.brand,
            "hotelchain": contact.hotel.chain.name,
            "hotelname": contact.hotel.property_name,
            "url": contact.hotel.url,
            "custom[0]": contact.id
        }
        data = self._api_call('PUT', uri, params)
        return data["data"]["id"]
