import re
import requests
from datetime import datetime, timedelta

class AccessToken(object):
    """wraps access token to APIs"""
    def __init__(self):
        self.uri = 'https://authorization.go.com/token'
        self.params = {
            'grant_type': 'assertion',
            'assertion_type': 'public',
            'client_id': 'WDPRO-MOBILE.CLIENT-PROD'
        }
        self.renew()

    def renew(self):
        """resets token and expiration window"""
        result = requests.post(self.uri, self.params)
        data = result.json()
        self.token = data['access_token']
        valid_seconds = int(data['expires_at'])
        self.expires_at = datetime.now() + timedelta(seconds=valid_seconds)

    @property
    def is_expired(self):
        """determines if token has expired"""
        return self.expires_at <= datetime.now()


class Ride(object):
    """models a ride at a park"""
    def __init__(self, id, name, url, queue_time, status, fastpass_eligible, single_rider_available):
        self.id = id
        self.name = name
        self.url = url
        self.queue_time_minutes = queue_time
        self.status = status
        self.fastpass_eligible = fastpass_eligible
        self.single_rider_eligible = single_rider_available

    @classmethod
    def from_json(cls, json):
        """builds object from JSON response"""
        name = json['name']
        status = json['waitTime']['status']
        queue_time = int(json['waitTime']['postedWaitMinutes'])
        fastpass_eligible = json['waitTime']['fastPass']['available']
        single_rider_available = json['waitTime']['singleRider']
        response_id = json['id']
        if ';' in response_id:
            id = response_id.split(';')[0]
        else:
            id = response_id
        url = json['links']['attractions']['href']
        return cls(id, name, url, queue_time, status, fastpass_eligible, single_rider_available)

class Character(object):
    def __init__(self, id, name):
        'https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/characters/90004846'
        self.id = id
        self.name = name

    @classmethod
    def from_json(self, json):
        response_id = json['id']
        if ';' in response_id:
            self.id = response_id.split(';')[0]
        else:
            self.id = response_id
        self.name = json['name']

    @classmethod
    def from_uri(cls, access_token, uri):
        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=access_token),
            'Accept': 'application/json;apiversion=1',
            'X-Conversation-Id': '~WDPRO-MOBILE.CLIENT-PROD'
        }
        response = requests.get(uri, headers=headers)
        data = response.json()
        return cls.from_json(data)

class Location(object):
    def __init__(self, id, name, latitude, longitude):
        self.name = name
        self.id = id
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_json(cls, json):
        id = json['id']
        name = json['name']
        gps = json['coordinates']['Guest Entrance']['gps']
        latitude = gps['latitude']
        longitude = gps['longitude']
        return cls(id, name, latitude, longitude)

    @classmethod
    def from_uri(cls, access_token, uri):
        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=access_token),
            'Accept': 'application/json;apiversion=1',
            'X-Conversation-Id': '~WDPRO-MOBILE.CLIENT-PROD'
        }
        response = requests.get(uri, headers=headers)
        data = response.json()
        return cls.from_json(data)


class CharacterAppearance(object):
    def __init__(self, character, location, start_time, end_time):
        self.id = id
        self.character = character
        self.location = location
        self.start_time = start_time
        self.end_time = end_time


class Resort(object):
    """models resort"""
    def __init__(self, access_token, id):
        self.id = id
        self.access_token = access_token
        uri = 'https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/destinations/{id}'.format(
            id=self.id
        )
        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=access_token),
            'Accept': 'application/json;apiversion=1',
            'X-Conversation-Id': '~WDPRO-MOBILE.CLIENT-PROD'
        }
        response = requests.get(uri, headers=headers)
        data = response.json()
        self.name = data['name']

    def get_theme_parks(self):
        """gets theme parks in Destination"""
        if self.parks:
            return self.parks

        uri = 'https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/destinations/{id}/theme-parks'.format(
            id=self.id
        )
        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=self.access_token),
            'Accept': 'application/json;apiversion=1',
            'X-Conversation-Id': '~WDPRO-MOBILE.CLIENT-PROD'
        }
        response = requests.get(uri, headers=headers)
        data = response.json()
        park_urls = []
        for entry in data['entries']:
            park_urls.append(entry['links']['self']['href'])

        self.parks = []
        for url in park_urls:
            park_id = re.search('/(\d+)', url).groups()[0]
            self.parks.append(ThemePark(self.access_token, park_id))
        return self.parks

class ThemePark(object):
    """models Disney World park"""
    def __init__(self, access_token, park_id):
        self.id = park_id
        self.access_token = access_token
        uri = 'https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/theme-parks/{park_id}'.format(
            park_id=self.id
        )
        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=access_token),
            'Accept': 'application/json;apiversion=1',
            'X-Conversation-Id': '~WDPRO-MOBILE.CLIENT-PROD'
        }
        response = requests.get(uri, headers=headers)
        data = response.json()
        self.name = data['name']

    def get_rides(self):
        """gets a list of rides at the park"""
        if self.rides:
            return self.rides
        uri = 'https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/theme-parks/{park_id}/wait-times'.format(
            park_id=self.id
        )
        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=self.access_token),
            'Accept': 'application/json;apiversion=1',
            'X-Conversation-Id': '~WDPRO-MOBILE.CLIENT-PROD'
        }
        response = requests.get(uri, headers=headers)
        self.data = response.json()
        self.rides = []
        for entry in self.data['entries']:
            self.rides.append(Ride.from_json(entry))
        return self.rides

    def get_character_appearances(self):
        """gets characters appearing in the park and where/when to meet them"""
        uri = 'https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/theme-parks/{id}/character-appearances'.format(
            id=self.id,
        )
        headers = {
            'Authorization': "BEARER {access_token}".format(access_token=self.access_token),
            'Accept': 'application/json;apiversion=1',
            'X-Conversation-Id': '~WDPRO-MOBILE.CLIENT-PROD'
        }
        response = requests.get(uri, headers=headers)
        data = response.json()
        characters = {}
        locations = {}
        self.character_appearances = []
        for entry in data['entries']:
            character_url = entry['character']['links']['self']['href']
            if character_url not in characters.keys():
                characters[character_url] = Character.from_uri(self.access_token, character_url)
            character = characters[character_url]
            appearances = entry['appearances']
            for appearance in appearances:
                start_time = appearance['startTime']
                end_time = appearance['endTime']
                location_element = appearance['locations'][0]
                location_url = location_element['links']['self']['href']
                if location_url not in locations.keys():
                    locations[location_url] = Location.from_uri(self.access_token, location_url)
                location = locations[location_url]
                self.character_appearances.append(CharacterAppearance(character, location, start_time, end_time))
        return self.character_appearances