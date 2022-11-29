import gpxpy
from .utils import distance

# Segments are sequences of points, no need to do any internal processing on gpxpy segments, it's the same deal.
#  

# The space between two points is either moving or stopped, this is very easy to identify, can create tripples of (start, end, speed), call this a step
def get_steps(points):
    steps = [] # (startpt, endpt, speed)

    for i in range(1, len(points)):
        previous = points[i - 1]
        point = points[i]

        delta_time = point.time - previous.time
        delta_time_in_seconds = delta_time.total_seconds()   # TODO figure out what to do if time delta is zero, shouldn't happen practically
        delta_distance = distance(point.longitude, point.latitude, previous.longitude, previous.latitude)
        speed = delta_distance / delta_time_in_seconds
        steps.append((previous, point, speed))

    return steps

# Helper takes [(start, end)] and returns [points]
def steps_to_points(steps):
    points = []
    for (start, end) in steps: 
        
        if(len(points) == 0):
            points.append(start)
            points.append(end)
        else:
            if(not points[-1] == start):
                points.append(start)
            if(not points[-1] == end):
                points.append(end)    
    return points


# Adjacent steps that are all moving or stopped are a segment, a segment is either moving or stopped, (isMoving, [points])
def steps_to_segments(steps, stopped_threshold_speed):

    # 1: Identify segments and keep track of the steps in each
    segments_with_steps = []  # (isStopped, [(pt1, pt2)])
    current_segment_steps = []

    for (pt1, pt2, speed) in steps:
        step_stopped = speed < stopped_threshold_speed
        step = (pt1, pt2)

        if(len(current_segment_steps) == 0):
            current_segment_steps.append(step)
        else:
            (current_segment_stopped, _) = current_segment_steps[-1]

            if(not current_segment_stopped == step_stopped):
                segments_with_steps.append((current_segment_stopped, current_segment_steps))
                current_segment_steps = []
            
            current_segment_steps.append(step)

    (current_segment_stopped, _) = current_segment_steps[-1]
    segments_with_steps.append((current_segment_stopped, current_segment_steps))

    # 2: Collapse the steps into points, avoid duplication
    segments_with_points = []
    for (isStopped, steps) in segments_with_steps:
        segments_with_points.append((isStopped, steps_to_points(steps)))
    return segments_with_points

# Segments can be marked as break or non break (isBreak, [points]) based on elapsed time
def mark_segments_as_breaks(segments, break_duration_threshold):

    result = []

    for (isStopped, points) in segments:
        elapsed_time = points[-1].time - points[0].time
        is_long_enough_to_be_break = elapsed_time.total_seconds() > break_duration_threshold
        result.append((is_long_enough_to_be_break and isStopped, points))

    return result

# Adjacent non-break segments can be merged by concatinating points [(isBreak, points)] -> [(isBreak, points)]
def concat_nonbreak_segments(segments):
    result = []

    for (isBreak, points) in segments:
        if(len(result) == 0):
            result.append((isBreak, points))
        else:
            (last_segment_is_break, _) = result[-1]
            if(not last_segment_is_break and not isBreak):
                result[-1][1].extend(points[1:])
            else:
                result.append((isBreak, points))

    return result

# Putting it all together
def split_breaks(points, stopped_threshold_speed, break_duration_threshold):
    steps = get_steps(points)
    segments_marked_as_stopped = steps_to_segments(steps, stopped_threshold_speed)
    segments_marked_as_breaks = mark_segments_as_breaks(segments_marked_as_stopped, break_duration_threshold)
    concated_segments = concat_nonbreak_segments(segments_marked_as_breaks)
    return concated_segments

if __name__ == "__main__":
    print(concat_nonbreak_segments([
        (True, ['a', 'b', 'c']),
        (False, ['c', 'd', 'e']),
        (False, ['e', 'f', 'g']),
        (True, ['g', 'h', 'i']),
    ]))