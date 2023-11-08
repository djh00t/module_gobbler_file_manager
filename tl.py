#!/Users/djh/miniconda3/envs/module_klingon_file_manager/bin/python

"""
This script provides a command-line interface to repeatedly run a pytest test file at specified intervals,
re-reading the file if its contents change.

Usage:
    test_runner.py [-h] -t TEST -s SECONDS

Arguments:
    -t TEST, --test TEST       Specify the path to the pytest test file to run.
    -s SECONDS, --seconds SECONDS
                               Specify the frequency, in seconds, of how often to run the test.
    -h, --help                 Show this help message and exit.

The script will continuously run the specified pytest test every given number of seconds.
It will report the duration of each test run and provide a countdown timer for the next test run.
The script will only exit when a KeyboardInterrupt (Ctrl-C) is received.
"""

import argparse
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

def get_file_modification_time(file_path):
    """
    Gets the last modification time of a file.

    Parameters:
        file_path (str): The path to the file.

    Returns:
        float: The last modification time of the file.
    """
    # Extract the file path without the test function
    file_only_path = file_path.split("::")[0]
    return os.path.getmtime(file_only_path)


def run_test(test_path, last_mod_time):
    """
    Runs the pytest on the specified test file and checks for file modification.

    Parameters:
        test_path (str): The path to the pytest test file and optionally the specific test function.
        last_mod_time (float): The last known modification time of the test file.

    Returns:
        tuple: A tuple containing the duration the test took to run, the exit code,
               and the new modification time of the test file.
    """
    # Extract the file path without the test function
    file_only_path = test_path.split("::")[0]
    current_mod_time = get_file_modification_time(file_only_path)

    if current_mod_time != last_mod_time:
        print(
            f"\nDetected changes in '{file_only_path}'. Re-running the test.\n"
        )

    start_time = datetime.now()
    result = subprocess.run(["pytest", test_path])
    end_time = datetime.now()
    return (
        (end_time - start_time).total_seconds(),
        result.returncode,
        current_mod_time,
    )


def countdown(test_path, frequency, duration):
    """
    Displays a countdown timer for the specified duration in seconds along with the test name and frequency.

    Parameters:
        test_path (str): The path to the pytest test file.
        frequency (int): The frequency, in seconds, that the script was called with.
        duration (int): The countdown duration in seconds.
    """
    test_name = test_path.split('/')[-1]  # Extract the test file name
    target_time = datetime.now() + timedelta(seconds=duration)
    while datetime.now() < target_time:
        time_left = target_time - datetime.now()
        minutes, seconds = divmod(time_left.total_seconds(), 60)
        timer_output = "\rNext test in:\t\t\t\t\t\t{:02}:{:02}".format(
            int(minutes), int(seconds)
        )
        sys.stdout.write(timer_output)
        sys.stdout.flush()
        time.sleep(1)
    print("\n")


def main(test, frequency):
    """
    The main function of the script that sets up the test run loop.

    Parameters:
        test (str): The path to the pytest test file.
        frequency (int): The frequency, in seconds, of how often to run the test.
    """
    last_mod_time = get_file_modification_time(test)
    try:
        while True:
            test_duration, exit_code, last_mod_time = run_test(test, last_mod_time)
            test_name = test.split('/')[-1]  # Extract the test file name
            if exit_code == 0:
                print(f"{test_name}:\tPASS\nFrequency:\t\t\t\t\t\t{frequency}s\nTook:\t\t\t\t\t\t\t{test_duration:.2f} seconds to run")
            else:
                print(f"{test_name}:\tFAIL\nFrequency:\t\t\t\t\t\t{frequency}s\nTook:\t\t\t\t\t\t\t{test_duration:.2f} seconds to run")

            countdown(test, frequency, frequency)
    except KeyboardInterrupt:
        print("\nExiting due to Ctrl-C")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a pytest test repeatedly at set intervals, checking for file changes."
    )
    parser.add_argument(
        "-t",
        "--test",
        required=True,
        help="Specify the pytest test file to run.",
    )
    parser.add_argument(
        "-s",
        "--seconds",
        type=int,
        required=True,
        help="Specify the frequency, in seconds, to run the test.",
    )
    args = parser.parse_args()

    main(args.test, args.seconds)
