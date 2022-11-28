import pyproj 

# returns elipsoid distance between start and end location specified in degrees, returns result in meters
def distance(long1, lat1, long2, lat2):
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth,back_azimuth,distance = geodesic.inv(long1, lat1, long2, lat2)
    return distance