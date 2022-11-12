from math import atan, radians, degrees
import click
import gpxpy
import gpxpy.gpx
import gisutil
import munterfuncs
from tabulate import tabulate

SECONDS_PER_HOUR = 60 * 60

@click.command()
@click.argument('gpxfile', type=click.File('r'))
@click.option('--chunk-length', default=50.0, show_default=True, help="Length of chunk in meters that track is broken into for analysis. Defaults to value that caltopo uses.")
@click.option('--grade-cutoff', default=5, show_default=True, help="Grade in degrees used to decide if a chunk is uphill, downhill, or flat.")
def muntertool(gpxfile, chunk_length, grade_cutoff):
    """Analyze the track described by GPXFILE"""
    # TODO: Better docs here

    # Parse the GPX file
    try:
        gpx = gpxpy.parse(gpxfile)
    except:
        raise click.UsageError("Error: Failed to parse GPX file. Check that the file is not corrupted.", ctx=None)

    # Validate that the GPX contains exactly one track, TODO: support multi-track gpx files
    if(not len(gpx.tracks) == 1):
        raise click.UsageError("Error: GPX file must contain exactly one track. Found {} tracks.".format(len(gpx.tracks)), ctx=None)
    track = gpx.tracks[0]

    # Break track into chunks
    chunks = []
    for segment in track.segments:
        chunks.extend(chunkify(segment, chunklength=chunk_length))
    
    if(not len(chunks) > 0):
        raise click.UsageError("Error: Could not extract chunks from track.".format(len(gpx.tracks)), ctx=None)

    # Chunk report 
    print(chunk_report(chunks, grade_cutoff))

def chunk_report(chunks, grade_cutoff):
    headers = ["Start Point", "End Point", "Distance", "Elevation", "Time", "Grade", "Category", "Munter Rate"]
    table = []

    for chunk in chunks: 
        pt_fmt_str = "({}, {})"
        st_pt = pt_fmt_str.format(chunk.first_point.longitude, chunk.first_point.latitude)
        end_pt = pt_fmt_str.format(chunk.last_point.longitude, chunk.last_point.latitude)
        category = grade_classification(chunk, grade_cutoff)
        table.append([st_pt, end_pt, chunk.distance, chunk.delta_elevation, chunk.delta_time, formatted_grade(chunk.grade), category, chunk.munter_rate])

    return(tabulate(table, headers, tablefmt="plain"))

class Chunk: 
    def __init__(self, first_point, last_point, distance):
        self.first_point = first_point
        self.last_point = last_point
        self.distance = distance

        self.delta_elevation = self.last_point.elevation - self.first_point.elevation 
        self.delta_time = self.last_point.time - self.first_point.time
        self.munter_rate = munterfuncs.munter_reverse(self.distance, self.delta_elevation, self.delta_time.total_seconds()/SECONDS_PER_HOUR)

        self.grade = degrees(atan(self.delta_elevation/self.distance))

    def __repr__(self):
        return "Chunk(first point {}, last point {}, distance {}".format(
            self.first_point,
            self.last_point,
            self.distance)

def chunkify(segment, chunklength=50):
    chunks = []

    current_chunk_distance = 0
    current_chunk_beginning_point = None 
    current_chunk_last_point = None

    for point in segment.points: 
        if(current_chunk_beginning_point == None):
            current_chunk_beginning_point = point 
            current_chunk_last_point = point 
            continue 

        current_chunk_distance += gisutil.distance(current_chunk_last_point.longitude, current_chunk_last_point.latitude, point.longitude, point.latitude)
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


if __name__ == '__main__':
    muntertool()