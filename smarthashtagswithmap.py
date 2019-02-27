import math
from typing import List, Any

import requests
import json


class Instapy(object):
    def __init__(self, *args, **kwargs):
        self.smart_hashtags = None

    def location_to_lonlat(self, location):  # Get LON and LAT from Instagram Explorer
        base_url = 'https://www.instagram.com/explore/locations/'
        query_url = '{}{}{}'.format(base_url, location, "?__a=1")
        req = requests.get(query_url)
        data = json.loads(req.text)

        lat = data['graphql']['location']['lat']
        lon = data['graphql']['location']['lng']
        # print(lat_, lon_)
        
        return lat, lon

    def get_bounding_box(self, latitude_in_degrees, longitude_in_degrees, half_side_in_miles):
        assert half_side_in_miles > 0
        assert latitude_in_degrees >= -90.0 and latitude_in_degrees <= 90.0
        assert longitude_in_degrees >= -180.0 and longitude_in_degrees <= 180.0

        half_side_in_km = half_side_in_miles * 1.609344
        lat = math.radians(latitude_in_degrees)
        lon = math.radians(longitude_in_degrees)

        radius = 6371
        # Radius of the parallel at given latitude
        parallel_radius = radius * math.cos(lat)

        lat_min = lat - half_side_in_km / radius
        lat_max = lat + half_side_in_km / radius
        lon_min = lon - half_side_in_km / parallel_radius
        lon_max = lon + half_side_in_km / parallel_radius

        lat_min = rad2deg(lat_min)
        lon_min = rad2deg(lon_min)
        lat_max = rad2deg(lat_max)
        lon_max = rad2deg(lon_max)
        
        bbox = {
            lat_min: lat_min,
            lat_max: lat_max,
            lon_min: lon_min,
            lon_max: lon_max
        }

        return bbox

    def set_smart_hashtags_map(self,
                               location,
                               zoom,
                               miles,
                               limit=3,
                               log_tags=True):
        """Generate smart hashtags based on https://displaypurposes.com/map"""
        lat, lon = self.location_to_lonlat(location)

        bbox = self.get_bounding_box(lat, lon, half_side_in_miles=miles)

        bbox_url = '{},{},{},{}&zoom={}'.format(bbox.lon_min, bbox.lat_min, bbox.lon_max,
                                            bbox.lat_max, zoom)
        url = '{}{}'.format('https://query.displaypurposes.com/local/?bbox=', bbox_url)
        
        req = requests.get(url)
        data = json.loads(req.text)
        if int(data['count']) > 0:  # Get how many hashtags we got
            count = data['count']
            i = 0
            tags: List[Any] = []
            while i < count:
                tags.append(data['tags'][i]['tag'])  # Adding each hashtag to the list
                i += 1
            self.smart_hashtags = (tags[:limit])  # Limit the number of #

            if log_tags is True:
                print(u'[smart hashtag generated: {}]'.format(self.smart_hashtags))
            return self
        else:
            print(u'Too few results for #{} tag'.format(data['count']))


# From Instagram Location to displaypurposes/map Feature

box = Instapy()
box.set_smart_hashtags_map("204517928/chicago-illinois", zoom=50, miles=10, limit=10, log_tags=True)
                        ###"""Instagram Location-     ,Zoom map, boundaries, # Limit, Log or not"""
