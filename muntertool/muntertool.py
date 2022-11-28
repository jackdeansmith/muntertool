from math import atan, radians, degrees
import click
import gpxpy
import gpxpy.gpx
from tabulate import tabulate
import pyproj
from tqdm import tqdm
import math
import functools
from .utils import break_remove
from .utils.distance import distance

SECONDS_PER_HOUR = 60 * 60

@click.command()
@click.argument('gpxfile', type=click.File('r'))
@click.option('--chunk-length', default=50.0, show_default=True, help="Length of chunk in meters that track is broken into for analysis.")
@click.option('--grade-cutoff', default=5, show_default=True, help="Grade in degrees used to decide if a chunk is uphill, downhill, or flat.")
@click.option("--percentile", multiple=True, default=[0.5], help="Calculate this percentile for each chunk type. Multiple uses allowed. [default: 0.5]")
@click.option('--progress', is_flag=True, default=False, help="Show a progress bar as gpx points are processed")
def stats(gpxfile, chunk_length, grade_cutoff, progress, percentile):
    """Analyze GPXFILE and output rate statistics."""

    track = shared_parse_gpx_track(gpxfile)
    chunks = chunkify_track(track, chunklength=chunk_length, show_progress=progress)
    
    if(not len(chunks) > 0):
        raise click.UsageError("Error: Could not extract chunks from track.", ctx=None)

    # Statistical report 
    print(statistical_report(chunks, grade_cutoff, percentile))

@click.command()
@click.argument('gpxfile', type=click.File('r'))
@click.option('--chunk-length', default=50.0, show_default=True, help="Length of chunk in meters that track is broken into for analysis.")
@click.option('--grade-cutoff', default=5, show_default=True, help="Grade in degrees used to decide if a chunk is uphill, downhill, or flat.")
@click.option('--showcordinates', is_flag=True, default=False, help="Show the start and end cordinates for each chunk")
@click.option('--progress', is_flag=True, default=False, help="Show a progress bar as gpx points are processed")
def chunks(gpxfile, chunk_length, grade_cutoff, showcordinates, progress):
    """Break GPXFILE into chunks and output details."""

    track = shared_parse_gpx_track(gpxfile)
    chunks = chunkify_track(track, chunklength=chunk_length, show_progress=progress)
    
    if(not len(chunks) > 0):
        raise click.UsageError("Error: Could not extract chunks from track.", ctx=None)

    # Statistical report 
    print(chunk_report(chunks, grade_cutoff, showcordinates))

def shared_parse_gpx_track(gpxfile):
    # Parse the GPX file
    try:
        gpx = gpxpy.parse(gpxfile)
    except:
        raise click.UsageError("Error: Failed to parse GPX file. Check that the file is not corrupted.", ctx=None)

    # Validate that the GPX contains exactly one track
    if(not len(gpx.tracks) == 1):
        raise click.UsageError("Error: GPX file must contain exactly one track. Found {} tracks.".format(len(gpx.tracks)), ctx=None)
    track = gpx.tracks[0]

    return track

def chunk_report(chunks, grade_cutoff, showcordinates):
    headers = ["Chunk"] 
    if(showcordinates):
        headers.extend(["Start", "End"])
    headers.extend(["Distance", "Elevation", "Time", "Grade", "Category", "Munter Rate"])

    table = []

    for (idx, chunk) in enumerate(chunks): 
        pt_fmt_str = "({:.7f}, {:.7f})"
        st_pt = pt_fmt_str.format(chunk.first_point.longitude, chunk.first_point.latitude)
        end_pt = pt_fmt_str.format(chunk.last_point.longitude, chunk.last_point.latitude)
        category = grade_classification(chunk, grade_cutoff)

        tabledata = [idx]
        if(showcordinates):
            tabledata.extend([st_pt, end_pt])
        tabledata.extend([chunk.distance, chunk.delta_elevation, chunk.delta_time, formatted_grade(chunk.grade), category, chunk.munter_rate])
        table.append(tabledata)

    return tabulate(table, headers, tablefmt="simple")

def statistical_report(chunks, grade_cutoff, desired_percentiles=[0.5]):

    # Classify all the chunks 
    up_chunks = []
    flat_chunks = []
    down_chunks = []
    for chunk in chunks:
        classification = grade_classification(chunk, grade_cutoff)
        if(classification == "UP"):
            up_chunks.append(chunk)
        elif(classification == "FLAT"):
            flat_chunks.append(chunk)
        elif(classification == "DOWN"):
            down_chunks.append(chunk)

    up_rates = [x.munter_rate for x in up_chunks]
    flat_rates = [x.munter_rate for x in flat_chunks]
    down_rates = [x.munter_rate for x in  down_chunks]

    mean_uphill_munter = maybe_mean_pretty_print(up_rates)
    mean_flat_munter = maybe_mean_pretty_print(flat_rates)
    mean_downhill_munter = maybe_mean_pretty_print(down_rates)

    percentile_headers = [pretty_print_percentile_header(x) for x in desired_percentiles]
    headers = ["Grade", "#Chunks", "Mean Rate"] + percentile_headers

    table = []
    table.append(["UP", len(up_chunks), mean_uphill_munter] + maybe_percentiles_pretty_print(up_rates, desired_percentiles))
    table.append(["FLAT", len(flat_chunks), mean_flat_munter]+ maybe_percentiles_pretty_print(flat_rates, desired_percentiles))
    table.append(["DOWN", len(down_chunks), mean_downhill_munter] + maybe_percentiles_pretty_print(down_rates, desired_percentiles))
    return tabulate(table, headers, tablefmt="simple")

def pretty_print_percentile_header(num):
    return "{}th Percentile Rate".format(num * 100)

def maybe_mean_pretty_print(nums):
    if(len(nums) == 0):
        return "-"
    else:
        return mean(nums)

def mean(nums):
    return sum(nums) / len(nums)

def maybe_percentiles_pretty_print(data, desired_percentiles):
    if(len(data) == 0):
        return ["-" for _ in desired_percentiles]
    else:
        return percentiles(data, desired_percentiles)

def percentiles(data, desired_percentiles):
    data.sort()
    results = []
    for x in desired_percentiles: 
        results.append(percentile(data, x))
    return results

def percentile(N, percent, key=lambda x:x):
   if not N:
       return None
   k = (len(N)-1) * percent
   f = math.floor(k)
   c = math.ceil(k)
   if f == c:
       return key(N[int(k)])
   d0 = key(N[int(f)]) * (c-k)
   d1 = key(N[int(c)]) * (k-f)
   return d0+d1

class Chunk: 
    def __init__(self, first_point, last_point, distance):
        self.first_point = first_point
        self.last_point = last_point
        self.distance = distance

        self.delta_elevation = self.last_point.elevation - self.first_point.elevation 
        self.delta_time = self.last_point.time - self.first_point.time
        self.munter_rate = munter_reverse(self.distance, self.delta_elevation, self.delta_time.total_seconds()/SECONDS_PER_HOUR)

        self.grade = degrees(atan(self.delta_elevation/self.distance))

    def __repr__(self):
        return "Chunk(first point {}, last point {}, distance {}".format(
            self.first_point,
            self.last_point,
            self.distance)

def chunkify_track(track, chunklength=50, show_progress=True):
    chunks = []
    for segment in track.segments:
        chunks.extend(chunkify_segment(segment, chunklength=chunklength, show_progress=show_progress))
    return chunks

def chunkify_segment(segment, chunklength=50, show_progress=True):
    chunks = []

    # break_remove.split_by_breaks(segment)

    current_chunk_distance = 0
    current_chunk_beginning_point = None 
    current_chunk_last_point = None

    for point in tqdm(segment.points, desc="Processing Points", disable=not show_progress): 
        if(current_chunk_beginning_point == None):
            current_chunk_beginning_point = point 
            current_chunk_last_point = point 
            continue 

        current_chunk_distance += distance(current_chunk_last_point.longitude, current_chunk_last_point.latitude, point.longitude, point.latitude)
        current_chunk_last_point = point

        if(current_chunk_distance >= chunklength):
            chunks.append(Chunk(current_chunk_beginning_point, current_chunk_last_point, current_chunk_distance))
            current_chunk_distance = 0
            current_chunk_beginning_point = current_chunk_last_point

    if(current_chunk_distance > 0):
        chunks.append(Chunk(current_chunk_beginning_point, current_chunk_last_point, current_chunk_distance))

    return chunks


def formatted_grade(grade):
    return "{:.1f}°".format(grade)

def grade_classification(chunk, grade_cutoff):
    if(chunk.grade > grade_cutoff):
        return "UP"
    elif(chunk.grade > -grade_cutoff):
        return "FLAT"
    else: 
        return "DOWN"

# Gets a time in hours from distance m, elevation in m, and dimensionless munter rate value
def munter_forward(distance, elevation, rate):
    return munter_work(distance, elevation) / rate

# Gets a munter rate value from a distance in m, elevation in m, and time
def munter_reverse(distance, elevation, time):
    return munter_work(distance, elevation) / time

# Accepts a distance and elevation and returns a munter work value, this is divided by rate to get time
def munter_work(distance, elevation):
 return ((distance/1000) + abs(elevation)/100)

@click.group()
def cli():
    pass

cli.add_command(stats)
cli.add_command(chunks)