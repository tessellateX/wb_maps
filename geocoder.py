class Geocoder(object):
    """docstring for geocoder."""
    def __init__(self, map_service='osm'):
        """
        map_service = 'osm', 'gmaps'
        """
        self.geocoder = self._init_coder(map_service)

    def _init_coder(self, map_service):
        if map_service == 'osm':
            from geopy.geocoders import Nominatim
            return Nominatim()
        else:
            from geopy.geocoders import GoogleV3
            with open('api_key.txt', 'r') as f:
                api_key = f.read()
            return GoogleV3(api_key=api_key)

    def geocode(self, addr):
        try:
            return self.geocoder.geocode(addr, timeout=2)
        except Exception as e:
            print('{0} for addr {1}'.format(e, addr))
            return None
