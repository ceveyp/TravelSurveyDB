import sys
from pathlib import Path
from typing import Dict

import pandas as pd
from pandas import DataFrame

from constants.spreadsheet.column_names.contacts import ContactsColumnNamesEnum
from db.models import HotelChain, Hotel
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

    def read(self):
        # Read contacts sheet
        self._dfs = pd.read_excel(self._file_path)
        rows = self._dfs.to_dict(orient="records")

        hotel_chain_key_entity_map: Dict[str, HotelChain] = {}

        for row in rows:
            # Get row hotel chain
            hotel_chain_name = get_field(row, ContactsColumnNamesEnum.CHAIN_NAME, str)
            hotel_chain_key = normalize_field(hotel_chain_name)
            if hotel_chain_key_entity_map.get(hotel_chain_key):
                hotel_chain = hotel_chain_key_entity_map[hotel_chain_key]
            else:
                hotel_chain = HotelChain(
                    chain_name=hotel_chain_name,
                    brand_name=get_field(row, ContactsColumnNamesEnum.BRAND_NAME, str)
                )
                hotel_chain_key_entity_map[hotel_chain_key] = hotel_chain

            hotel = Hotel(
                cvent_id=get_field(row, ContactsColumnNamesEnum.CVENT_ID, int),
                property_name=get_field(row, ContactsColumnNamesEnum.PROPERTY_NAME, str),
                address=get_field(row, ContactsColumnNamesEnum.ADDRESS, str),
                city=get_field(row, ContactsColumnNamesEnum.CITY, str),
                state=get_field(row, ContactsColumnNamesEnum.STATE, str),
                country=get_field(row, ContactsColumnNamesEnum.COUNTRY, str),
                postal_code=get_field(row, ContactsColumnNamesEnum.POSTAL_CODE, str),
                phone=get_field(row, ContactsColumnNamesEnum.P)
            )
            hotel.chain = hotel_chain








if __name__ == '__main__':
    ContactsSpreadsheetReader(r"C:/Users/phili/Documents/Jobs/TravelDB/contacts.xlsx").read()
