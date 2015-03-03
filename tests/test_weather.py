from eemeter.weather import WeatherSourceBase
from eemeter.weather import GSODWeatherSource
from eemeter.weather import ISDWeatherSource
from eemeter.weather import TMY3WeatherSource
from eemeter.weather import WeatherUndergroundWeatherSource
from eemeter.weather import zipcode_to_lat_lng
from eemeter.weather import lat_lng_to_zipcode
from eemeter.weather import tmy3_to_lat_lng
from eemeter.weather import lat_lng_to_tmy3
from eemeter.weather import zipcode_to_tmy3
from eemeter.weather import tmy3_to_zipcode
from eemeter.weather import haversine

from eemeter.consumption import ConsumptionHistory
from eemeter.consumption import Consumption

from datetime import datetime
import pytest
import os
import warnings

from numpy.testing import assert_almost_equal

EPSILON = 10e-6

##### Fixtures #####

@pytest.fixture
def consumption_history_one_summer_electricity():
    c_list = [Consumption(1600,"kWh","electricity",datetime(2012,6,1),datetime(2012,7,1)),
              Consumption(1700,"kWh","electricity",datetime(2012,7,1),datetime(2012,8,1)),
              Consumption(1800,"kWh","electricity",datetime(2012,8,1),datetime(2012,9,1))]
    return ConsumptionHistory(c_list)

@pytest.fixture(params=[(41.8955360374983,-87.6217660821178,"725340"),
                        (34.1678563835543,-118.126220490392,"722880"),
                        (42.3769095103979,-71.1247640734676,"725090"),
                        (42.3594006437094,-87.8581578622419,"725347")])
def lat_long_station(request):
    return request.param

@pytest.fixture(params=[(41.8955360374983,-87.6217660821178,"60611"),
                        (34.1678563835543,-118.126220490392,"91104"),
                        (42.3769095103979,-71.1247640734676,"02138"),
                        (42.3594006437094,-87.8581578622419,"60085"),
                        (None,None,"00000")])
def lat_long_zipcode(request):
    return request.param

@pytest.fixture(params=[('722874-93134',2012,2012),
                        ('722874',2012,2012)])
def gsod_weather_source(request):
    return request.param

@pytest.fixture(params=[('722874-93134',2012,2012),
                        ('722874',2012,2012)])
def isd_weather_source(request):
    return request.param

@pytest.fixture(params=[TMY3WeatherSource('722880')])
def tmy3_weather_source(request):
    return request.param

@pytest.fixture(params=[("60611","725340"),
                        ("91104","722880"),
                        ("02138","725090"),
                        ("60085","725347")])
def zipcode_to_station(request):
    return request.param


##### Tests #####

def test_zipcode_to_lat_lng(lat_long_zipcode):
    lat_lngs = [(41.8955360374983,-87.6217660821178),
               (34.1678563835543,-118.126220490392),
               (42.3769095103979,-71.1247640734676),
               (42.3594006437094,-87.8581578622419)]
    zipcodes = ["60611","91104","02138","60085"]
    for (lat,lng),zipcode in zip(lat_lngs,zipcodes):
        assert lat,lng == zipcode_to_lat_lng(zipcode)

def test_lat_lng_to_zipcode():
    lat_lngs = [(41.8955360374983,-87.6217660821178),
               (34.1678563835543,-118.126220490392),
               (42.3769095103979,-71.1247640734676),
               (42.3594006437094,-87.8581578622419)]
    zipcodes = ["60611","91104","02138","60085"]
    for (lat,lng),zipcode in zip(lat_lngs,zipcodes):
        assert zipcode == lat_lng_to_zipcode(lat,lng)

def test_tmy3_to_lat_lng():
    lat_lngs = [(41.8955360374983,-87.6217660821178),
               (34.1678563835543,-118.126220490392),
               (42.3769095103979,-71.1247640734676),
               (42.3594006437094,-87.8581578622419)]
    stations = ["725340","722880","725090","725347"]
    for (lat,lng),station in zip(lat_lngs,stations):
        assert lat,lng == tmy3_to_lat_lng(station)

def test_lat_lng_to_tmy3():
    lat_lngs = [(41.8955360374983,-87.6217660821178),
               (34.1678563835543,-118.126220490392),
               (42.3769095103979,-71.1247640734676),
               (42.3594006437094,-87.8581578622419)]
    stations = ["725340","722880","725090","725347"]
    for (lat,lng),station in zip(lat_lngs,stations):
        assert station == lat_lng_to_tmy3(lat,lng)

def test_zipcode_to_tmy3():
    zipcodes = ["60611","91104","02138","60085"]
    stations = ["725340","722880","725090","725347"]
    for zipcode,station in zip(zipcodes,stations):
        assert station == zipcode_to_tmy3(zipcode)

def test_tmy3_to_zipcode():
    zipcodes = ["97459","45433","55601","96740"]
    stations = ["726917","745700","727556","911975"]
    for zipcode,station in zip(zipcodes,stations):
        assert zipcode == tmy3_to_zipcode(station)

def test_weather_source_base(consumption_history_one_summer_electricity):
    weather_source = WeatherSourceBase()
    consumptions = consumption_history_one_summer_electricity.get("electricity")
    with pytest.raises(NotImplementedError):
        avg_temps = weather_source.get_average_temperature(consumptions,"degF")
    with pytest.raises(NotImplementedError):
        hdds = weather_source.get_hdd(consumptions,"degF",base=65)

@pytest.mark.slow
@pytest.mark.internet
def test_gsod_weather_source(consumption_history_one_summer_electricity,gsod_weather_source):
    gsod_weather_source = GSODWeatherSource(*gsod_weather_source)
    consumptions = consumption_history_one_summer_electricity.get("electricity")
    avg_temps = gsod_weather_source.get_average_temperature(consumptions,"degF")
    assert abs(avg_temps[0] - 66.3833333333) < EPSILON
    assert abs(avg_temps[1] - 67.8032258065) < EPSILON
    assert abs(avg_temps[2] - 74.4451612903) < EPSILON
    hdds = gsod_weather_source.get_hdd(consumptions,"degF",65)
    assert abs(hdds[0] - 0.7) < EPSILON
    assert abs(hdds[1] - 20.4) < EPSILON
    assert abs(hdds[2] - 0.0) < EPSILON
    cdds = gsod_weather_source.get_cdd(consumptions,"degF",65)
    assert abs(cdds[0] - 42.2) < EPSILON
    assert abs(cdds[1] - 107.3) < EPSILON
    assert abs(cdds[2] - 292.8) < EPSILON

@pytest.mark.slow
@pytest.mark.internet
def test_weather_underground_weather_source(consumption_history_one_summer_electricity):
    wunderground_api_key = os.environ.get('WEATHERUNDERGROUND_API_KEY')
    if wunderground_api_key:
        wu_weather_source = WeatherUndergroundWeatherSource('60605',
                                                            datetime(2012,6,1),
                                                            datetime(2012,10,1),
                                                            wunderground_api_key)
        consumptions = consumption_history_one_summer_electricity.get("electricity")
        avg_temps = wu_weather_source.get_average_temperature(consumptions,"degF")
        assert abs(avg_temps[0] - 74.4333333333) < EPSILON
        assert abs(avg_temps[1] - 82.6774193548) < EPSILON
        assert abs(avg_temps[2] - 75.4516129032) < EPSILON
        hdds = wu_weather_source.get_hdd(consumptions,"degF",65)
        assert abs(hdds[0] - 14.0) < EPSILON
        assert abs(hdds[1] - 0.0) < EPSILON
        assert abs(hdds[2] - 0.0) < EPSILON
        cdds = wu_weather_source.get_cdd(consumptions,"degF",65)
        assert abs(cdds[0] - 297.0) < EPSILON
        assert abs(cdds[1] - 548.0) < EPSILON
        assert abs(cdds[2] - 324.0) < EPSILON
    else:
        warnings.warn("Skipping WeatherUndergroundWeatherSource tests. "
            "Please set the environment variable "
            "WEATHERUNDERGOUND_API_KEY to run the tests.")

@pytest.mark.slow
@pytest.mark.internet
def test_isd_weather_source(consumption_history_one_summer_electricity,isd_weather_source):
    isd_weather_source = ISDWeatherSource(*isd_weather_source)
    consumptions = consumption_history_one_summer_electricity.get("electricity")
    avg_temps = isd_weather_source.get_average_temperature(consumptions,"degF")
    assert abs(avg_temps[0] - 66.576956521739135) < EPSILON
    assert abs(avg_temps[1] - 68.047780898876411) < EPSILON
    assert abs(avg_temps[2] - 74.697162921348323) < EPSILON
    hdds = isd_weather_source.get_hdd(consumptions,"degF",65)
    assert abs(hdds[0] - 0.29478220869567906) < EPSILON
    assert abs(hdds[1] - 20.309999600000033) < EPSILON
    assert abs(hdds[2] - 0.0) < EPSILON
    cdds = isd_weather_source.get_cdd(consumptions,"degF",65)
    assert abs(cdds[0] - 47.603489860868635) < EPSILON
    assert abs(cdds[1] - 113.77566417391201) < EPSILON
    assert abs(cdds[2] - 300.72214678735065) < EPSILON

@pytest.mark.slow
@pytest.mark.internet
def test_tmy3_weather_source(consumption_history_one_summer_electricity,tmy3_weather_source):
    consumptions = consumption_history_one_summer_electricity.get("electricity")
    normal_avg_temps = tmy3_weather_source.get_average_temperature(consumptions,"degF")
    assert abs(normal_avg_temps[0] - 68.411913043478265) < EPSILON
    assert abs(normal_avg_temps[1] - 73.327545582047691) < EPSILON
    assert abs(normal_avg_temps[2] - 74.593604488078540) < EPSILON
    normal_hdds = tmy3_weather_source.get_hdd(consumptions,"degF",65)
    assert abs(normal_hdds[0] - 8.6582576695655149) < EPSILON
    assert abs(normal_hdds[1] - 0.0) < EPSILON
    assert abs(normal_hdds[2] - 0.0) < EPSILON
    normal_cdds = tmy3_weather_source.get_cdd(consumptions,"degF",65)
    assert abs(normal_cdds[0] - 111.01566097391235) < EPSILON
    assert abs(normal_cdds[1] - 258.15392544347725) < EPSILON
    assert abs(normal_cdds[2] - 297.40175153043384) < EPSILON

def test_haversine():
    lat_lng_dists = [(0,0,0,0,0),
                     (76,1,76,1,0),
                     (76,1,76,361,0),
                     (0,0,0,90,10007.54339801),
                     (0,0,0,180,20015.08679602),
                     (0,-180,0,180,0),
                     (-90,0,90,0,20015.08679602),
                     (-90,0,90,180,20015.08679602),
                     ]

    for lat1,lng1,lat2,lng2,dist in lat_lng_dists:
        assert_almost_equal(haversine(lat1,lng1,lat2,lng2),dist)

