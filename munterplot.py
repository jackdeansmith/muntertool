import gpxpy
import gpxpy.gpx
from itertools import tee
import gisutil
from munterfuncs import munter_reverse, munter_work


# Parsing an existing file:
# -------------------------

gpx_file = open('/Users/jackdsmith/Desktop/track-10221-033955.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

# accepts a gpx track and returns tuples of adjacent points. Does not consider points in different segments to be adjacent as these could be separated by the subject moving. 
def track_to_point_pairs(track):
    point_pairs = []
    for segment in track.segments:
        point_pairs.extend(adjacent_pairs(segment.points))
    return point_pairs

def total_track_time(track):
    firstpoint = track.segments[0][0]
    lastpoint = track.segments[-1][-1]

    timedelta = lastpoint.time - firstpoint.time
    return timedelta


# Accepts iter([1,2,3,4,5]), returns iter([(1, 2), (2, 3), (3, 4), (4, 5)])
def adjacent_pairs(iterable):
    first_it, second_it = tee(iter(iterable))
    try:
        next(second_it)
    except StopIteration:
      return []
    return zip(first_it, second_it)

def pt_pair_to_munter_rate(pt1, pt2):
    distance = gisutil.distance(pt1.longitude, pt1.latitude, pt2.longitude, pt2.latitude)
    distance_in_km = distance/1000
    elevation = abs(pt1.elevation - pt2.elevation)
    timedelta = pt2.time - pt1.time
    timedelta_inhours = timedelta.total_seconds() / (60 * 60)
    return munter_reverse(distance_in_km, elevation, timedelta_inhours)
    print('distance: {}, elevation: {}, timedelta: {}'.format(distance, elevation, timedelta_inhours))

def pt_pair_to_munter_work(pt1, pt2):
    distance = gisutil.distance(pt1.longitude, pt1.latitude, pt2.longitude, pt2.latitude)
    distance_in_km = distance/1000
    elevation = abs(pt1.elevation - pt2.elevation)
    return munter_work(distance_in_km, elevation)

rates = []
total_work = 0
for track in gpx.tracks:
    point_pairs = track_to_point_pairs(track)
    for (pt1, pt2) in point_pairs:
        # print('Point at ({0},{1}) -> {2} @{3}'.format(point.latitude, point.longitude, point.elevation, point.time))
        print('Pair: ({},{}) ({},{})'.format(pt1.latitude, pt1.longitude, pt2.latitude, pt2.longitude,))
        rate = pt_pair_to_munter_rate(pt1, pt2)
        rates.append(rate)

        work = pt_pair_to_munter_work(pt1, pt2)
        total_work += work

        print("RATE = {}".format(rate))
        print("WORK = {}".format(work))
        print()

# Note: Produces an "Average Rate" of 16 for my sample data. Clearly weighting by "point" is a bad idea. Maybe each should be weighted by effort?
print("Average Rate: {}".format(sum(rates)/len(rates)))
print("Total Work: {}".format(total_work))

print(total_track_time(track).total_seconds())



# Some other ideas: 
# Accumulate all the "munter work" for a track, segment of track, etc... then use the total leg time to get a munter rate. 
# Weight by the 

# print(list(adjacent_pairs([1,2])))