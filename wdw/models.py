import requests
from datetime import datetime, timedelta

class AccessToken(object):
    """wraps access token to APIs"""
    uri = 'https://authorization.go.com/token'
    params = {
        'grant_type': 'assertion',
        'assertion_type': 'public',
        'client_id': 'WDPRO-MOBILE.MDX.WDW.ANDROID-PROD'
    }
    def __init__(self):
        self.renew()

    def renew(self):
        """resets token and expiration window"""
        result = requests.post(self.uri, self.params)
        data = result.json()
        self.token = data['access_token']
        valid_seconds = int(data['expires_in'])
        self.expires_at = datetime.now() + timedelta(seconds=valid_seconds)

    @property
    def is_expired(self):
        """determines if token has expired"""
        return self.expires_at <= datetime.now()


class Ride():
    """models a ride at a park"""
    def __init__(self, id, name, url, queue_time, status, fastpass_eligible, single_rider_available):
        self.id = id
        self.name = name
        self.url = url
        self.queue_time_minutes = queue_time
        self.status = status
        self.fastpass_eligible = fastpass_eligible
        self.single_rider_eligible = single_rider_available

    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, json):
        """builds object from JSON response"""
        print(json)
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
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

    @classmethod
    def from_json(self, json):
        response_id = json['id']
        if ';' in response_id:
            self.id = response_id.split(';')[0]
        else:
            self.id = response_id
        self.name = json['name']


class Location(object):
    def __init__(self, id, name, latitude, longitude):
        self.name = name
        self.id = id
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, json):
        id = json['id']
        name = json['name']
        gps = json['coordinates']['Guest Entrance']['gps']
        latitude = gps['latitude']
        longitude = gps['longitude']
        return cls(id, name, latitude, longitude)


class CharacterAppearance(object):
    def __init__(self, character, location, start_time, end_time):
        self.id = id
        self.character = character
        self.location = location
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return '%s at %s from %s - %s' % (
            self.character,
            self.location,
            self.start_time,
            self.end_time
        )

class Resort(object):
    """models resort"""
    def __init__(self, resort_id, name, description):
        self.id = resort_id
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, data):
        resort_id = data['id']
        name = data['name']
        description = data['descriptions']['shortDescription']['text']
        return cls(resort_id, name, description)


class ThemePark(object):
    """models theme park"""
    def __init__(self, park_id, name):
        self.id = park_id
        self.name = name

    def __str__(self):
        return self.name

    @classmethod
    def from_json(cls, data):
        theme_park_id = str(data['id'])
        if ';' in theme_park_id:
            theme_park_id = theme_park_id.split(';')[0]
        name = data['name']
        return cls(theme_park_id, name)


class WaltDisneyWorldResort(Resort):
    """creates special case Resort for Walt Disney World"""
    def __init__(self):
        super(WaltDisneyWorldResort, self).__init__(
            80007798,
            'Walt Disney World Resort',
            'Walt Disney World Resort is a vacation wonderland that includes 4 theme parks, '
            + '2 water parks and over 20 Resort hotels\u2014plus world-class shopping, dining, '
            + 'entertainment, recreation, sports and much, much more. Visit an enchanted kingdom, '
            + 'explore the world of today and tomorrow, star in a Hollywood movie and venture into '
            + 'exotic realm filled with amazing animals. Find out why this really is the place where '
            + 'dreams come true!'
        )
