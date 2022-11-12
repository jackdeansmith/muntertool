import click
import gpxpy
import gpxpy.gpx
import gisutil
import munterfuncs

SECONDS_PER_HOUR = 60 * 60

@click.command()
@click.argument('gpxfile', type=click.File('r'))
def muntertool(gpxfile):
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

    munterstats(track)

def munterstats(track, chunklength=50):
    """Accepts a gpx track and breaks it into 'chunks' for munter analysis, analyzes each chunk."""

    chunks = []
    for segment in track.segments:
        chunks.extend(chunkify(segment))

    for chunk in chunks: 
        # print(chunk)
        munter_rate = munterfuncs.munter_reverse(chunk.distance, chunk.delta_elevation(), chunk.delta_time().total_seconds()/SECONDS_PER_HOUR)
        print(munter_rate)

class Chunk: 
    def __init__(self, first_point, last_point, distance):
        self.first_point = first_point
        self.last_point = last_point
        self.distance = distance

    def delta_elevation(self):
        return self.last_point.elevation - self.first_point.elevation

    def delta_time(self):
        return self.last_point.time - self.first_point.time

    def __repr__(self):
        return "Chunk(first point {}, last point {}, distance {}".format(
            self.first_point,
            self.last_point,
            self.distance)

def chunkify(segment, chunklength=50):
    
    #TODO: Assert segment has at least two points

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


if __name__ == '__main__':
    muntertool()