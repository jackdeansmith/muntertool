# test the munter work function
import muntertool.muntertool as muntertool
import pytest

def test_munter_work():
    # Elevation gain and loss counts the same
    assert muntertool.munter_work(1000, 100) == pytest.approx(muntertool.munter_work(1000, -100))

    # Linearity
    assert muntertool.munter_work(3, 5) + muntertool.munter_work(7, 11) == pytest.approx(muntertool.munter_work(10, 16))

    # Zero distance and zero elevation are valid inputs 
    muntertool.munter_work(0,1) 
    muntertool.munter_work(1,0) 

def test_munter_forward_reverse_identity():
    # Test that munter_forward and munter_reverse are inverses of each other
    distance = 1000
    elevation = 100
    time = 1

    rate = muntertool.munter_reverse(distance, elevation, time)
    assert muntertool.munter_forward(distance, elevation, rate) == pytest.approx(time)

def test_munter_example_data():
    # Test that munter_forward works with the example data
    # Source: https://backcountryaccess.com/en-us/blog/p/how-to-calculate-backcountry-touring-time-based-distance-elevation-gain
    # Source is very inexact, I have done the math by hand myself

    distance = 4 * 1000 # Distance in meters
    elevation = 1000
    time = 3.5
    rate = 4

    run_forward_test(distance, elevation, time, rate)
    run_backward_test(distance, elevation, time, rate)

def run_forward_test(distance, elevation, time, rate):
    assert muntertool.munter_forward(distance, elevation, rate) == pytest.approx(time)

def run_backward_test(distance, elevation, time, rate):
    assert muntertool.munter_reverse(distance, elevation, time) == pytest.approx(rate)
