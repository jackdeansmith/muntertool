import gpxpy
import gpxpy.gpx

# Parsing an existing file:
# -------------------------

gpx_file = open('/Users/jackdsmith/Desktop/track-10221-033955.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print('Point at ({0},{1}) -> {2} @{3}'.format(point.latitude, point.longitude, point.elevation, point.time))
