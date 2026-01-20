import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
from pandas import DataFrame

from constants.spreadsheet.column_names.contacts import ContactsColumnNamesEnum
from db.models import HotelChain, Hotel
from db.models.hotel import HotelContact
from utils.common import get_field, normalize_field
from utils.logger import get_logger

logger = get_logger()


class ContactsSpreadsheetReader:

    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            logger.error(f"Could not find file: {file_path}")
            sys.exit(1)
        self._dfs: DataFrame | None = None

    def read(self) -> List[Hotel]:
        # Read contacts sheet
        self._dfs = pd.read_excel(self._file_path)
        rows = self._dfs.to_dict(orient="records")

        hotel_chain_key_entity_map: Dict[str, HotelChain] = {}
        hotels = []
        column_names = ContactsColumnNamesEnum

        for i, row in enumerate(rows):
            try:
                # Get row hotel chain
                hotel_chain_name = get_field(row, column_names.CHAIN_NAME, str)
                hotel_chain_key = normalize_field(hotel_chain_name)
                if hotel_chain_key_entity_map.get(hotel_chain_key):
                    hotel_chain = hotel_chain_key_entity_map[hotel_chain_key]
                else:
                    hotel_chain = HotelChain(
                        name=hotel_chain_name,
                        brand=get_field(row, column_names.BRAND_NAME)
                    )
                    hotel_chain_key_entity_map[hotel_chain_key] = hotel_chain

                # Create hotel
                hotel = Hotel(
                    cvent_id=get_field(row, column_names.CVENT_ID, int),
                    property_name=get_field(row, column_names.PROPERTY_NAME),
                    address=get_field(row, column_names.ADDRESS),
                    city=get_field(row, column_names.CITY),
                    state=get_field(row, column_names.STATE),
                    country=get_field(row, column_names.COUNTRY),
                    postal_code=get_field(row, column_names.POSTAL_CODE),
                    phone=get_field(row, column_names.MAIN_PHONE),
                    url=get_field(row, column_names.HOTEL_WEBSITE)
                )
                hotel.chain = hotel_chain
                hotels.append(hotel)

                # Create contacts
                sales_associate = HotelContact(
                    name=get_field(row, column_names.SALES_ASSOCIATE_NAME, default=''),
                    title=get_field(row, column_names.SALES_ASSOCIATE_TITLE, default=''),
                    email=get_field(row, column_names.SALES_ASSOCIATE_EMAIL, default=''),
                    phone=get_field(row, column_names.SALES_ASSOCIATE_PHONE, default=''),
                    role="sales_associate"
                )
                hotel.contacts.append(sales_associate)

                account_manager = HotelContact(
                    name=get_field(row, column_names.ACCOUNT_MANAGER_NAME, default=''),
                    title="Account Manager",
                    email=get_field(row, column_names.ACCOUNT_MANAGER_EMAIL, default=''),
                    role="account_manager"
                )
                hotel.contacts.append(account_manager)

            except Exception as e:
                logger.exception(e)
                logger.error(f"There was an error parsing contacts list, row {i}: {e}")
        return hotels
