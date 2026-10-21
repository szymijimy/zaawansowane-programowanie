import argparse
import requests

class Brewery:
    def __init__(self, data: dict):
        self.id: str = data.get("id")
        self.name: str = data.get("name")
        self.brewery_type: str = data.get("brewery_type")
        self.address_1: str = data.get("address_1")
        self.address_2: str = data.get("address_2")
        self.address_3: str = data.get("address_3")
        self.city: str = data.get("city")
        self.state_province: str = data.get("state_province")
        self.postal_code: str = data.get("postal_code")
        self.country: str = data.get("country")
        self.longitude: str = data.get("longitude")
        self.latitude: str = data.get("latitude")
        self.phone: str = data.get("phone")
        self.website_url: str = data.get("website_url")
        self.state: str = data.get("state")
        self.street: str = data.get("street")

    def __str__(self) -> str:
        return f"Browar: {self.name} | Typ: {self.brewery_type} | Miasto: {self.city}, {self.country} | Tel: {self.phone}"

parser = argparse.ArgumentParser(description="Pobieranie listy browarów")
parser.add_argument("--city", type=str, help="Filtruj browary po miastach")
args = parser.parse_args()

url = "https://api.openbrewerydb.org/v1/breweries?per_page=20"

if args.city:
    formatted_city = args.city.replace(" ", "_")
    url += f"&by_city={formatted_city}"

response = requests.get(url)
data = response.json()

breweries = [Brewery(item) for item in data]

for brewery in breweries:
    print(brewery)