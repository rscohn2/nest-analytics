from collector.collector import filter_event


def test_filter_event_no_resource():
    temperatures = {}
    humidities = {}
    event = {}
    assert filter_event(event, temperatures, humidities)


def test_filter_event_temperature_change():
    temperatures = {"thermostat1": 22.0}
    humidities = {}
    event = {
        "resourceUpdate": {
            "name": "thermostat1",
            "traits": {
                "sdm.devices.traits.Temperature": {
                    "ambientTemperatureCelsius": 22.5
                }
            },
        }
    }
    assert filter_event(event, temperatures, humidities)
    assert temperatures["thermostat1"] == 22.5


def test_filter_event_temperature_no_change():
    temperatures = {"thermostat1": 22.0}
    humidities = {}
    event = {
        "resourceUpdate": {
            "name": "thermostat1",
            "traits": {
                "sdm.devices.traits.Temperature": {
                    "ambientTemperatureCelsius": 22.1
                }
            },
        }
    }
    assert not filter_event(event, temperatures, humidities)
    assert temperatures["thermostat1"] == 22.0


def test_filter_event_humidity_change():
    temperatures = {}
    humidities = {"thermostat1": 40}
    event = {
        "resourceUpdate": {
            "name": "thermostat1",
            "traits": {
                "sdm.devices.traits.Humidity": {"ambientHumidityPercent": 42}
            },
        }
    }
    assert filter_event(event, temperatures, humidities)
    assert humidities["thermostat1"] == 42


def test_filter_event_humidity_no_change():
    temperatures = {}
    humidities = {"thermostat1": 40}
    event = {
        "resourceUpdate": {
            "name": "thermostat1",
            "traits": {
                "sdm.devices.traits.Humidity": {"ambientHumidityPercent": 40.5}
            },
        }
    }
    assert not filter_event(event, temperatures, humidities)
    assert humidities["thermostat1"] == 40
