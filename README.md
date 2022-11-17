# Muntertool

Muntertool is a python command line tool for reading GPS tracks and finding the Munter Method rate parameters for that track. 

## Purpose

The Munter method is a technique to take a cross country travel route and estimate the time it will take to travel using the topography of the route and a set of customizable rate parameters. This technique often produces useful estimates and is integrated directly into popular mapping tools like CalTopo. The basic formula for munter method estimation is: 

```
TIME [hours] = DISTANCE [km] + ((ELEVATION [meters]/100)) / RATE)
```

Since rate is variable by grade, a different rate parameter is used for Uphill, Flat, and Downhill segments. For example, Caltopo defaults to rate parameters (UP=4 FLAT=6 DOWN=10) for backcountry skiing and (UP=4 FLAT=6 DOWN=6) for hiking on a trail. Since every group travels at a different pace, these parameters usually have to be tweaked to get more accurate estimates. The purpose of this tool is to assist that guesswork by taking an actual recording from a previous trip and analyzing the track to show your munter rates. These rates can then be plugged back into the formula when planning a future trip. 

## Install

Install muntertool directly from this repo by running: 

```
$ python -m pip install "git+https://github.com/jackdeansmith/muntertool"
```

You can then run muntertool directly:
```
$ muntertool --help
```

## Usage 

```
Usage: muntertool [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  chunks  Break GPXFILE into chunks and output details.
  stats   Analyze GPXFILE and output rate statistics.
```

## `muntertool stats`

stats breaks your file into chunks, classifies those chunks by their grade, and calcualtes summary statistics. 
By default, the chunk-length and grade-cutoff parameters are the same ones used by Caltopo so the rates are directly comparable. 

```
Usage: muntertool stats [OPTIONS] GPXFILE

  Analyze GPXFILE and output rate statistics.

Options:
  --chunk-length FLOAT    Length of chunk in meters that track is broken into
                          for analysis.  [default: 50.0]
  --grade-cutoff INTEGER  Grade in degrees used to decide if a chunk is
                          uphill, downhill, or flat.  [default: 5]
  --percentile FLOAT      Calculate this percentile for each chunk type.
                          Multiple uses allowed. [default: 0.5]
  --progress              Show a progress bar as gpx points are processed
  --help                  Show this message and exit.
```


Example, simple analysis: 
```
$ muntertool stats ExampleData/TrailRun.gpx
Grade      #Chunks    Mean Rate    50.0th Percentile Rate
-------  ---------  -----------  ------------------------
UP              46      11.1854                   11.0837
FLAT            34      13.1513                   12.754
DOWN            68      24.9152                   25.3367
```

Example, getting conservative 20th percentile estimate: 
```
$ muntertool stats ExampleData/TrailRun.gpx --percentile .2 --percentile .5
Grade      #Chunks    Mean Rate    20.0th Percentile Rate    50.0th Percentile Rate
-------  ---------  -----------  ------------------------  ------------------------
UP              46      11.1854                   10.3015                   11.0837
FLAT            34      13.1513                   11.201                    12.754
DOWN            68      24.9152                   22.266                    25.3367
```

## `muntertool chunks`

chunks breaks your track into chunks and prints the information about every single chunk. It's useful if you want to see the distribution of rates or do your own analysis. 

Example: Show all the chunks used to calculate munter rates for a trail run
```
$ muntertool chunks ExampleData/ShortTrailRun.gpx
  Chunk    Distance    Elevation  Time     Grade    Category      Munter Rate
-------  ----------  -----------  -------  -------  ----------  -------------
      0     51.9948            7  0:00:52  7.7°     UP                8.44579
      1     55.2028           17  0:01:14  17.1°    UP               10.9558
      2     57.5539           14  0:01:09  13.7°    UP               10.3072
      3     58.1904           22  0:01:42  20.7°    UP                9.81849
      4     57.1072           19  0:01:33  18.4°    UP                9.56544
      5     55.9127           21  0:02:27  20.6°    UP                6.51215
      6     70.3727           29  0:02:48  22.4°    UP                7.72227
      7     50.4321            7  0:10:01  7.9°     UP                0.72139
      8     58.6931          -12  0:00:32  -11.6°   DOWN             20.103
      9     75.2313           -8  0:01:00  -6.1°    DOWN              9.31388
     10     81.741            -5  0:00:26  -3.5°    FLAT             18.2411
     11     65.0443           -7  0:00:22  -6.1°    DOWN             22.0982
     12     55.8014           -9  0:00:28  -9.2°    DOWN             18.7459
     13     85.2872           -5  0:00:54  -3.4°    FLAT              9.01914
     14     58.1878          -18  0:00:36  -17.2°   DOWN             23.8188
     15     54.8248          -17  0:00:36  -17.2°   DOWN             22.4825
     16     51.3016          -14  0:00:29  -15.3°   DOWN             23.7478
```

Example: Show all the chunks used to calculate munter rates for a trail run and show start and end points for each chunk
```
$ muntertool chunks ExampleData/ShortTrailRun.gpx --showcordinates
  Chunk  Start                       End                           Distance    Elevation  Time     Grade    Category      Munter Rate
-------  --------------------------  --------------------------  ----------  -----------  -------  -------  ----------  -------------
      0  (-120.7060764, 48.6941843)  (-120.7055795, 48.6944802)     51.9948            7  0:00:52  7.7°     UP                8.44579
      1  (-120.7055795, 48.6944802)  (-120.7051350, 48.6948639)     55.2028           17  0:01:14  17.1°    UP               10.9558
      2  (-120.7051350, 48.6948639)  (-120.7047126, 48.6952632)     57.5539           14  0:01:09  13.7°    UP               10.3072
      3  (-120.7047126, 48.6952632)  (-120.7042211, 48.6956084)     58.1904           22  0:01:42  20.7°    UP                9.81849
      4  (-120.7042211, 48.6956084)  (-120.7038888, 48.6960668)     57.1072           19  0:01:33  18.4°    UP                9.56544
      5  (-120.7038888, 48.6960668)  (-120.7035100, 48.6964223)     55.9127           21  0:02:27  20.6°    UP                6.51215
      6  (-120.7035100, 48.6964223)  (-120.7030980, 48.6969418)     70.3727           29  0:02:48  22.4°    UP                7.72227
      7  (-120.7030980, 48.6969418)  (-120.7026837, 48.6971308)     50.4321            7  0:10:01  7.9°     UP                0.72139
      8  (-120.7026837, 48.6971308)  (-120.7019108, 48.6972488)     58.6931          -12  0:00:32  -11.6°   DOWN             20.103
      9  (-120.7019108, 48.6972488)  (-120.7009376, 48.6973775)     75.2313           -8  0:01:00  -6.1°    DOWN              9.31388
     10  (-120.7009376, 48.6973775)  (-120.6998594, 48.6975271)     81.741            -5  0:00:26  -3.5°    FLAT             18.2411
     11  (-120.6998594, 48.6975271)  (-120.6989766, 48.6975518)     65.0443           -7  0:00:22  -6.1°    DOWN             22.0982
     12  (-120.6989766, 48.6975518)  (-120.6982461, 48.6974178)     55.8014           -9  0:00:28  -9.2°    DOWN             18.7459
     13  (-120.6982461, 48.6974178)  (-120.6971219, 48.6975453)     85.2872           -5  0:00:54  -3.4°    FLAT              9.01914
     14  (-120.6971219, 48.6975453)  (-120.6964779, 48.6972659)     58.1878          -18  0:00:36  -17.2°   DOWN             23.8188
     15  (-120.6964779, 48.6972659)  (-120.6958755, 48.6970033)     54.8248          -17  0:00:36  -17.2°   DOWN             22.4825
     16  (-120.6958755, 48.6970033)  (-120.6952226, 48.6968485)     51.3016          -14  0:00:29  -15.3°   DOWN             23.7478
```