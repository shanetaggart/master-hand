"""
The helper functions for the Master Hand Discord bot.
"""

from datetime import datetime
import json
import os.path

# Global configuration and log filenames.
mh_config_file = "master_hand_configuration.json"
mh_log_file = "log.txt"


def create_necessary_files():
    """
    Creates the configuration and log files.
    """

    write_log("create_necessary_files", "process started", "arguments: null")

    # Set flags for the existence of required files.
    log_file_needed = not os.path.isfile(mh_log_file)
    config_file_needed = not os.path.isfile(mh_config_file)

    # When a log file is needed, create an empty one.
    if log_file_needed:
        f = open(mh_log_file, "w", encoding="utf-8")
        f.close()

        write_log(
            "create_necessary_files", "success", f"created the log file: {mh_log_file}"
        )

    # When a configuration file is nedded, create one with the default values.
    if config_file_needed:
        with open(mh_config_file, "w", encoding="utf-8") as f:
            f.write(
                '{"login_message": "Master Hand approaches!","base_role": "your_base_role", "command_role": "TOs"}'
            )

        write_log(
            "create_necessary_files",
            "success",
            f"created the configuration file: {mh_config_file}",
        )

    write_log("create_necessary_files", "process ended", "arguments: null")

    return


def set_configuration(key, value_to_set):
    """
    Set the specificed configuration value.
    """

    write_log(
        "set_configuration",
        "process started",
        f'arguments: key = "{key}",  value_to_set = "{value_to_set}"',
    )

    # Check if the configuration file exists.
    if os.path.isfile(mh_config_file):
        # Open the configuration file and set config to the JSON contents.
        with open(mh_config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Set the key to the value provided in the command.
        config[key] = value_to_set

        # Open the configuration file again and write the new JSON.
        with open(mh_config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        write_log(
            "set_configuration",
            "success",
            f'configuration object updated - "{key}": "{value_to_set}"',
        )

        write_log(
            "set_configuration",
            "process ended",
            f'arguments: key = "{key}",  value_to_set = "{value_to_set}"',
        )

        return
    else:
        write_log("set_configuration", "failure", "necessary files are missing")

        # If you somehow get here, create the necessary files.
        create_necessary_files()

        write_log(
            "set_configuration",
            "process ended",
            f'arguments: key = "{key}",  value_to_set = "{value_to_set}"',
        )

        return


def get_config(key):
    """
    Get the specificed configuration value.
    """

    write_log(
        "get_config",
        "process started",
        f'arguments: key = "{key}"',
    )

    # Check if the configuration file exists.
    if os.path.isfile(mh_config_file):
        # Open the configuration file and set config to the JSON contents.
        with open(mh_config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Get the value provided in the command if it exists.
        if key in config:
            value_to_retrieve = config[key]

            write_log("get_config", "success", f'pulled configuration for "{key}"')

            write_log(
                "get_config",
                "process ended",
                f'arguments: key = "{key}"',
            )

            return value_to_retrieve
        else:
            write_log(
                "get_config", "failure", f'configuration for "{key}" could not be found'
            )

            write_log(
                "get_config",
                "process ended",
                f'arguments: key = "{key}"',
            )

            return False


def write_log(action, status, log_text):
    """
    Write data to a log file in a standardized format.
    """

    # Set an empty array to hold the log data.
    log_data = []

    # Set the timestamp format to "01 January, 2024 - 15:49:05".
    timestamp = datetime.now().strftime("%d %B, %Y - %H:%M:%S")

    # Append the log data to the empty array.
    log_data.append(timestamp)
    log_data.append(action)
    log_data.append(status)
    log_data.append(log_text)

    # Add the log data to the log file, from the array, pipe (|) separated.
    with open("log.txt", "a", encoding="utf-8") as f:
        for key, data in enumerate(log_data):
            f.write(data)

            # Check if this is the last log data element.
            if key != len(log_data) - 1:
                # Add a pipe (|) to all list elements but the last one.
                f.write("|")
            else:
                # Add a new line (\n) to the last list element.
                f.write("\n")

    return


# def pull_frame_data(url, attack_type):
#     """
#     Pulls framedata from Ultimate Frame Data.
#     """

#     import requests

#     # Timeout the response if it takes longer than 10 seconds.
#     response = requests.get(url, timeout=10)

#     # Sanitize the response by removing carriage return characters
#     html = response.text
#     html = html.replace("\n", "").replace("\t", "").replace("\r", "")

#     # Split the response by the moves class.
#     move_containers = html.split('<div class="moves">')

#     # The first list element is the doctype, it is unnecessary.
#     del move_containers[0]

#     # List Index: 0 = ground
#     # List Index:  1 = aerial
#     # List Index:  2 = special
#     # List Index:  3 = grabs
#     # List Index:  4 = dodges/rolls
#     # List Index:  5 = misc

#     ground_attacks = move_containers[0]
#     aerial_attacks = move_containers[1]
#     special_attacks = move_containers[2]
#     grabs = move_containers[3]
#     dodges_rolls = move_containers[4]
#     miscellaneous = move_containers[5]

#     if attack_type == "ground":
#         return ground_attacks
#     if attack_type == "aerial":
#         return aerial_attacks
#     if attack_type == "special":
#         return special_attacks
#     if attack_type == "grabs":
#         return grabs
#     if attack_type == "dodges":
#         return dodges_rolls
#     if attack_type == "misc":
#         return miscellaneous
