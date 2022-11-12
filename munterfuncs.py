
# Gets a time in hours from distance m, elevation in m, and dimensionless munter rate value
def munter_forward(distance, elevation, rate):
    return munter_work(distance, elevation) / rate

# Gets a munter rate value from a distance in m, elevation in m, and time
def munter_reverse(distance, elevation, time):
    return munter_work(distance, elevation) / time

# Accepts a distance and elevation and returns a munter work value, this is divided by rate to get time
def munter_work(distance, elevation):
 return ((distance/1000) + abs(elevation)/100)

 # TODO: add sanity checks to these functions
 # TODO: document properly
 # TODO: refactor to use timedelta objects for clarity