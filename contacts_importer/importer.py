from typing import Dict, List

from sqlmodel import select

from clients.google_maps import AddressValidator
from contacts_importer.reader import ContactsSpreadsheetReader
from db.models import Hotel, HotelChain
from db.orm import Session
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


class ContactsImporter:

    def __init__(self, db: Session, file_path: str):
        self._file_path = file_path
        self._db = db
        self._address_validator = AddressValidator()

    def _get_hotel_place_ids(self, hotels: List[Hotel]) -> Dict[str, Hotel]:
        hotels_place_id_entity_map: Dict[str, Hotel] = {}
        for hotel in hotels:
            address_line = f"{hotel.address}, {hotel.city}, {hotel.state}, {hotel.postal_code}, {hotel.country}"
            logger.debug(f"Importing for address line: {address_line}")
            try:
                place_id = self._address_validator.validate(address_line)
                hotel.place_id = place_id
            except Exception as e:
                logger.exception(e)
                logger.error(f"Error validating address, skipping: {address_line}")
                continue
            hotels_place_id_entity_map[place_id] = hotel
        return hotels_place_id_entity_map

    def _get_hotel_chain_name_entity_maps(self) -> Dict[str, HotelChain]:
        hotel_chain_name_entity_map: Dict[str, HotelChain] = {}
        hotel_chains: List[HotelChain] = self._db.query(HotelChain).all()
        for hotel_chain in hotel_chains:
            hotel_chain_name_entity_map[hotel_chain.name] = hotel_chain
        return hotel_chain_name_entity_map

    def import_contacts(self):
        # Read hotels/contacts spreadsheet
        logger.debug("Importing contacts")
        hotels = ContactsSpreadsheetReader(self._file_path).read()

        # Get place IDs from Google Maps
        hotels_place_id_entity_map = self._get_hotel_place_ids(hotels)

        # Get existing hotel chains
        hotel_chain_name_entity_map = self._get_hotel_chain_name_entity_maps()

        # Get existing place IDs
        hotel_place_ids = set(self._db.execute(select(Hotel.place_id)).scalars().all())

        imported_hotels = []
        imported_contacts = []

        for place_id, hotel in hotels_place_id_entity_map.items():
            if place_id in hotel_place_ids:
                continue

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

        self._db.commit()

        print(f"Imported {len(imported_hotels)} hotels and {len(imported_contacts)} contacts")
        print(f"Imported hotels: \n")
        for hotel in imported_hotels:
            print(f"\t{hotel.property_name}")
        print(f"\nImported contacts: \n")
        for contact in imported_contacts:
            print(f"\t{contact.name} - {contact.email}")


def import_contacts(file_path: str):
    with Session() as db:
        ContactsImporter(db, file_path).import_contacts()


if __name__ == '__main__':
    setup_logging()
    import_contacts(r"C:/Users/phili/Documents/Jobs/TravelDB/contacts_edit.xlsx")
