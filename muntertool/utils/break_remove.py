import gpxpy
from .distance import distance

def split_by_breaks(segment, stopped_speed_threshold=0.2777777778):
    """Accepts a gpx segment and a break speed threshold, returns (moving segments, stopped segments)"""

    moving_segments = []
    stopped_segments = []

    current_segment = []
    current_segment_moving = False

    for i in range(1, len(segment.points)):
        previous = segment.points[i - 1]
        point = segment.points[i]
        # chunk_speed = point.time

    return (moving_segments, stopped_segments)