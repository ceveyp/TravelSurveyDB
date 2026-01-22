import re
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
from email_validator import validate_email, EmailNotValidError
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

    @staticmethod
    def _validate_and_normalize_email(email: str) -> str:
        if not email:
            raise ValueError("Email is None")
        if not isinstance(email, str):
            raise ValueError(f"Emails is not right type: {email}")
        email = email.lower().strip()
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            raise ValueError(f"Could not validate email: {email}")
        return email

    @staticmethod
    def _split_contact_names(names_raw_text: str) -> List[str]:
        if re.findall(r' / ', names_raw_text):
            return names_raw_text.split('/')
        else:
            return [names_raw_text]

    def _split_contact_emails(self, email_raw_text: str) -> List[str]:
        normalized_emails = []
        if re.findall(r' / ', email_raw_text):
            emails = email_raw_text.split('/')
            for email in emails:
                normalized_emails.append(self._validate_and_normalize_email(email))
        else:
            normalized_emails = [self._validate_and_normalize_email(email_raw_text)]
        return normalized_emails

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
                    city=get_field(row, column_names.CITY, default=''),
                    state=get_field(row, column_names.STATE, default=''),
                    country=get_field(row, column_names.COUNTRY, default=''),
                    postal_code=get_field(row, column_names.POSTAL_CODE, default=''),
                    phone=get_field(row, column_names.MAIN_PHONE, default=''),
                    url=get_field(row, column_names.HOTEL_WEBSITE, default='')
                )
                hotel.chain = hotel_chain
                hotels.append(hotel)

                # Create contacts
                try:
                    sa_email = get_field(row, column_names.SALES_ASSOCIATE_EMAIL)
                    sa_email = self._validate_and_normalize_email(sa_email)
                    sales_associate = HotelContact(
                        name=get_field(row, column_names.SALES_ASSOCIATE_NAME, default=''),
                        title=get_field(row, column_names.SALES_ASSOCIATE_TITLE, default=''),
                        email=sa_email,
                        phone=get_field(row, column_names.SALES_ASSOCIATE_PHONE, default=''),
                        role="sales_associate"
                    )
                    hotel.contacts.append(sales_associate)
                except Exception as e:
                    logger.error(e)
                    logger.warning(f"There was an error adding sales associate for hotel {i} ({hotel.address})")

                # Split contact info when there are multiple contacts in one cell
                am_email_raw_text = get_field(row, column_names.ACCOUNT_MANAGER_EMAIL)
                names_raw_text = get_field(row, column_names.ACCOUNT_MANAGER_NAME)
                if not am_email_raw_text or not names_raw_text:
                    continue
                names = self._split_contact_names(names_raw_text)
                emails = self._split_contact_emails(am_email_raw_text)

                # Create account managers
                for contact_info in zip(names, emails):
                    account_manager = HotelContact(
                        name=contact_info[0],
                        title="Account Manager",
                        email=contact_info[1],
                        role="account_manager"
                    )
                    hotel.contacts.append(account_manager)

            except Exception as e:
                logger.exception(e)
                logger.error(f"There was an error parsing contacts list, row {i}: {e}")
        return hotels
