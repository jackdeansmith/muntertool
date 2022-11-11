
# Gets a time in hours from distance in km, elevation in m, and dimensionless munter rate value
def munter_forward(distance, elevation, rate):
    return (distance + elevation/100) / rate

# Gets a munter rate value from a distance in km, elevation in m, and time in hours
def munter_reverse(distance, elevation, time):
    return (distance + elevation/100) / time

# Accepts a distance and elevation and returns a munter work value, this is divided by rate to get time
def munter_work(distance, elevation):
 return (distance + elevation/100)