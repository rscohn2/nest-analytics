import yaml


def read_yaml(file_path):
    """Reads a YAML file and returns the content."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def write_yaml(data, file_path):
    """Writes data to a YAML file."""
    with open(file_path, "w") as file:
        yaml.dump(data, file, allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    input_file = "weather-events.yaml"
    output_file = "filtered-weather-events.yaml"

    # Read the YAML file
    events_in = read_yaml(input_file)

    events_out = []
    temperatures = {}
    humidities = {}
    for event in events_in:
        if "building" in event:
            del event["building"]
        event["structure"] = (
            "AVPHwEur9IypcgFobFu6bMvYqePUmR96S7vxIU018DtSWC"
            "-QNw3nQzvV6kR-npKIyeoqhI6IO2ufF3BSVDQp6rEMJGqWEQ"
        )
        events_out.append(event)

    # Write the new YAML file
    write_yaml(events_out, output_file)

    print(
        f"# input events: {len(events_in)}\n# output events: {len(events_out)}"
    )
    print(f"Filtered data saved to {output_file}")
