import click
import gpxpy
import gpxpy.gpx

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

    for segment in track.segments:
        for point in segment.points:
            print('Point at ({0},{1}) -> {2} @{3}'.format(point.latitude, point.longitude, point.elevation, point.time))


if __name__ == '__main__':
    muntertool()