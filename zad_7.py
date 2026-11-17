import requests


class Brewery:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.name = data.get("name")
        self.brewery_type = data.get("brewery_type")
        self.address_1 = data.get("address_1")
        self.address_2 = data.get("address_2")
        self.address_3 = data.get("address_3")
        self.city = data.get("city")
        self.state_province = data.get("state_province")
        self.postal_code = data.get("postal_code")
        self.country = data.get("country")
        self.longitude = data.get("longitude")
        self.latitude = data.get("latitude")
        self.phone = data.get("phone")
        self.website_url = data.get("website_url")
        self.state = data.get("state")
        self.street = data.get("street")

    def __str__(self):
        fields = [
            f"Nazwa {self.id}",
            str(self.name),
            str(self.brewery_type),
            str(self.address_1),
            str(self.address_2),
            str(self.city),
            str(self.state_province),
            str(self.postal_code),
            str(self.country),
            str(self.longitude),
            str(self.latitude),
            str(self.phone),
            str(self.website_url),
            str(self.state),
            f"{self.street} :)",
        ]
        return ", ".join(fields)


response = requests.get("https://api.openbrewerydb.org/v1/breweries")
data = response.json()

breweries = [Brewery(item) for item in data]

print(breweries)
