from datetime import datetime

import yaml


def read_yaml(file_path):
    """Reads a YAML file and returns the content."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def write_yaml(data, file_path):
    """Writes data to a YAML file."""
    with open(file_path, "w") as file:
        yaml.dump(data, file, allow_unicode=True, default_flow_style=False)


def filter_event(event, temperatures, humidities):
    resource = event.get("resourceUpdate")
    if not resource:
        return True

    thermostat = resource["name"]
    traits = resource["traits"]

    trait_v = traits.get("sdm.devices.traits.Temperature")
    if trait_v:
        previous = temperatures.get(thermostat)
        current = trait_v["ambientTemperatureCelsius"]
        if previous and abs(current - previous) < 0.25:
            return False
        temperatures[thermostat] = current
        return True

    trait_v = traits.get("sdm.devices.traits.Humidity")
    if trait_v:
        previous = humidities.get(thermostat)
        current = trait_v["ambientHumidityPercent"]
        if previous and abs(current - previous) < 1:
            return False
        humidities[thermostat] = current
        return True

    return True


if __name__ == "__main__":
    input_file = "nest-events.yaml"
    output_file = "filtered-nest-events.yaml"

    # Read the YAML file
    events_in = read_yaml(input_file)

    events_sorted = sorted(
        events_in, key=lambda x: datetime.fromisoformat(x["timestamp"])
    )

    events_out = []
    temperatures = {}
    humidities = {}
    for event in events_sorted:
        if "building" in event:
            del event["building"]
        if filter_event(event, temperatures, humidities):
            events_out.append(event)

    # Write the new YAML file
    write_yaml(events_out, output_file)

    print(
        f"# input events: {len(events_in)}\n# output events: {len(events_out)}"
    )
    print(f"Filtered data saved to {output_file}")
