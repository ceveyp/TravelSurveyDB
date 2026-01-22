from typing import Dict, List

from sqlmodel import select

from clients.google_maps import AddressValidator
from contacts_importer.reader import ContactsSpreadsheetReader
from db.models import Hotel, HotelChain
from db.models.hotel import HotelContact
from db.orm import Session
from utils.alchemer import Alchemer
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


class ContactsImporter:

    def __init__(self, db: Session, file_path: str, contact_list_name: str):
        self._file_path = file_path
        self._db = db
        self._address_validator = AddressValidator()
        self._alchemer_client = Alchemer()
        self._list_name = contact_list_name

    def _get_hotel_place_id(self, hotel: Hotel) -> str:
        address_line = f"{hotel.address}, {hotel.city}, {hotel.state}, {hotel.postal_code}, {hotel.country}"
        logger.debug(f"Importing for address line: {address_line}")
        try:
            place_id = self._address_validator.validate(address_line)
            hotel.place_id = place_id
        except Exception:
            raise RuntimeError(f"Error validating address, skipping: {address_line}")
        return place_id

    def _get_hotel_chain_name_entity_maps(self) -> Dict[str, HotelChain]:
        hotel_chain_name_entity_map: Dict[str, HotelChain] = {}
        hotel_chains: List[HotelChain] = self._db.query(HotelChain).all()
        for hotel_chain in hotel_chains:
            hotel_chain_name_entity_map[hotel_chain.name] = hotel_chain
        return hotel_chain_name_entity_map

    def _create_alchemer_contact_list(self) -> int:
        logger.debug("Creating contact list in Alchemer")
        logger.debug(f"List name: {self._list_name}")
        contact_list_id = self._alchemer_client.create_contact_list(self._list_name)
        logger.debug(f"Contact list ID: {contact_list_id}")
        return contact_list_id

    def _import_alchemer_contact(self, contact_list_id: int, contact: HotelContact):
        contact_id = self._alchemer_client.create_contact(contact_list_id, contact)
        logger.debug(f"Created Alchemer contact for {contact.email}: {contact_id}")

    def import_contacts(self):
        # Read hotels/contacts spreadsheet
        logger.debug("Importing contacts")
        hotels = ContactsSpreadsheetReader(self._file_path).read()

        # Get existing hotel chains
        hotel_chain_name_entity_map = self._get_hotel_chain_name_entity_maps()

        # Get existing place IDs
        existing_hotel_place_ids = set(self._db.execute(select(Hotel.place_id)).scalars().all())

        # Get existing cvent IDs
        existing_cvent_ids = set(self._db.execute(select(Hotel.cvent_id)).scalars().all())
        if None in existing_cvent_ids:
            existing_cvent_ids.remove(None)

        imported_hotels = []
        imported_contacts = []

        # Create contact list in Alchemer
        contact_list_id = self._create_alchemer_contact_list()

        for i, hotel in enumerate(hotels):
            try:
                # Filter by cvent ID
                if hotel.cvent_id in existing_cvent_ids:
                    logger.debug(f"cvent ID exists for hotel {hotel.property_name}, skipping")
                    continue

                # Get place IDs from Google Maps
                place_id = self._get_hotel_place_id(hotel)
                if place_id in existing_hotel_place_ids:
                    logger.debug(f"Place ID exists for hotel {hotel.property_name}, skipping")
                    continue
                existing_hotel_place_ids.add(place_id)

                # Create hotel chain if it does not exist
                if hotel_chain_name_entity_map.get(hotel.chain.name):
                    hotel.chain = hotel_chain_name_entity_map[hotel.chain.name]
                else:
                    self._db.add(hotel.chain)

                # Create hotel and contacts
                self._db.add(hotel)
                imported_hotels.append(hotel)
                for contact in hotel.contacts:
                    self._db.add(contact)
                    imported_contacts.append(contact)

                    # Add contact to Alchemer
                    self._import_alchemer_contact(contact_list_id, contact)

                self._db.commit()
            except Exception as e:
                logger.exception(e)
                logger.error(f"There was an error importing hotel {i}: {e}")
                logger.error(f"Hotel data: {hotel.model_dump()}")

        print(f"Imported {len(imported_hotels)} hotels and {len(imported_contacts)} contacts")
        print(f"Imported hotels: \n")
        for hotel in imported_hotels:
            print(f"\t{hotel.property_name}")
        print(f"\nImported contacts: \n")
        for contact in imported_contacts:
            print(f"\t{contact.name} - {contact.email}")


def import_contacts(file_path: str, contact_list_name: str):
    with Session() as db:
        ContactsImporter(db, file_path, contact_list_name).import_contacts()


if __name__ == '__main__':
    setup_logging()
    import_contacts(r"C:/Users/phili/Documents/Jobs/TravelDB/contacts.xlsx", "hotel-contacts-test")
