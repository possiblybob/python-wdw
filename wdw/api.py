"""defines interactions with WDW API"""
import json
import requests
from urllib.parse import urljoin
from .models import AccessToken, Character, CharacterAppearance, Location, Resort, Ride, ThemePark


class ApiClient(object):
    access_token = None
    base_url = 'https://api.wdpro.disney.go.com/facility-service/'
    base_url = 'https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/'

    def make_request(self, uri):
        """makes GET request to specified URL using valid access token"""
        if self.access_token is None:
            self.access_token = AccessToken()
        if self.access_token.is_expired:
            self.access_token.renew()

        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=self.access_token.token),
            'Accept': 'application/json'
        }
        response = requests.get(uri, headers=headers)
        return response.json()


class CharacterClient(ApiClient):
    """gets Character details from the API"""
    def get_by_id(self, character_id):
        """builds URL for getting character and retrieves it"""
        # TODO: build URL using format
        url = ''
        return self.get_by_url(url)

    def get_by_url(self, url):
        """retrieves Character from given URL"""
        data = self.make_request(url)
        return Character.from_json(data)


class CharacterAppearanceClient(ApiClient):
    def get_by_id(self, id):
        pass

    def get_by_url(self, url):
        pass

    def get_for_theme_park(self, theme_park):
        """gets characters appearing in the park and where/when to meet them"""
        uri = urljoin(
            self.base_url,
            'theme-parks/{id}/character-appearances'.format(
                id=theme_park.id
            )
        )
        character_client = CharacterClient()
        location_client = LocationClient()
        data = self.make_request(uri)
        # store characters/locations to limit API requests for duplicate information
        characters = {}
        locations = {}
        character_appearances = []
        for entry in data['entries']:
            character_url = entry['character']['links']['self']['href']
            if character_url not in characters.keys():
                characters[character_url] = character_client.get_by_url(character_url)
            character = characters[character_url]
            appearances = entry['appearances']
            for appearance in appearances:
                start_time = appearance['startTime']
                end_time = appearance['endTime']
                location_element = appearance['locations'][0]
                location_url = location_element['links']['self']['href']
                if location_url not in locations.keys():
                    locations[location_url] = location_client.get_by_url(location_url)
                location = locations[location_url]
                # combine retrieved data
                character_appearances.append(CharacterAppearance(character, location, start_time, end_time))
        return character_appearances


class LocationClient(ApiClient):
    """gets Location details from the API"""
    def get_by_id(self, location_id):
        """builds URL for getting location and retrieves it"""
        # TODO: build URL using format
        url = ''
        return self.get_by_url(url)

    def get_by_url(self, url):
        """retrieves Location from given URL"""
        data = self.make_request(url)
        return Location.from_json(data)


class ResortClient(ApiClient):
    """gets Resort details from the API"""
    def get_by_id(self, resort_id):
        uri = urljoin(
            self.base_url,
            'destinations/{id}'.format(
                id=resort_id
            )
        )
        return self.get_by_url(uri)

    def get_by_url(self, url):
        """retrieves Resort from given URL"""
        data = self.make_request(url)
        return Resort.from_json(data)


class RideClient(ApiClient):
    """get Ride details from the API"""
    def get_by_id(self, ride_id):
        pass

    def get_by_url(self, url):
        """retrieves Ride from the given URL"""
        data = self.make_request(url)
        return Ride.from_json(data)

    def get_for_theme_park(self, theme_park):
        """gets Rides within ThemePark"""
        uri = urljoin(
            self.base_url,
            'theme-parks/{id}/wait-times'.format(
                id=theme_park.id
            )
        )
        data = self.make_request(uri)
        rides = []
        for entry in data['entries']:
            rides.append(Ride.from_json(entry))
        return rides


class ThemeParkClient(ApiClient):
    def get_by_id(self, theme_park_id):
        """builds URL to ThemePark and requests"""
        uri = urljoin(
            self.base_url,
            'theme-parks/{id}'.format(
                id=theme_park_id
            )
        )
        return self.get_by_url(uri)

    def get_by_url(self, url):
        """retrieves ThemePark from given URL"""
        data = self.make_request(url)
        return ThemePark.from_json(data)

    def get_for_resort(self, resort):
        """gets theme parks associated with Resort"""
        uri = urljoin(
            self.base_url,
            'destinations/{id}/theme-parks'.format(
                id=resort.id
            )
        )
        data = self.make_request(uri)
        parks = []
        theme_park_client = ThemeParkClient()
        for entry in data['entries']:
            parks.append(theme_park_client.get_by_url(entry['links']['self']['href']))

        return parks