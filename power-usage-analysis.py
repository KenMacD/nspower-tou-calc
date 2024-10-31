#!/usr/bin/env python3

# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas",
# ]
# ///

import pandas as pd
from datetime import datetime
import argparse

# Rate constants ($ per kWh)
RATE_WINTER_PEAK = 0.34634
RATE_WINTER_OFF_PEAK = 0.17703
RATE_SUMMER = 0.12198
RATE_FIXED = 0.17703


def find_header_row(file_path):
    """
    Find the row number that contains the actual CSV headers.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        int: Row number of the actual CSV headers
    """
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            if line.strip().startswith("SERVICE,DATE,"):
                return i
    raise ValueError("Could not find the header row in the CSV file")


def analyze_power_usage(file_path):
    """
    Analyze power usage from CSV file based on specific time periods and seasons.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        dict: Dictionary containing usage sums and cost analysis
    """
    # Find the header row
    header_row = find_header_row(file_path)

    # Read the CSV file, skipping the metadata rows
    df = pd.read_csv(file_path, skiprows=header_row)

    # Convert DATE and START TIME columns to datetime, using American date format
    df["datetime"] = pd.to_datetime(
        df["DATE"] + " " + df["START TIME"], format="%m/%d/%Y %H:%M"
    )

    # Extract month and hour for filtering
    df["month"] = df["datetime"].dt.month
    df["hour"] = df["datetime"].dt.hour

    # Define winter months (November to March)
    winter_months = [11, 12, 1, 2, 3]

    # Define peak hours (7-11 and 17-21)
    peak_hours = list(range(7, 11)) + list(range(17, 21))

    # Calculate sums for different periods

    # 1. November to March during peak hours
    winter_peak = df[(df["month"].isin(winter_months)) & (df["hour"].isin(peak_hours))][
        "USAGE"
    ].sum()

    # 2. November to March outside peak hours
    winter_off_peak = df[
        (df["month"].isin(winter_months)) & (~df["hour"].isin(peak_hours))
    ]["USAGE"].sum()

    # 3. April to October (all hours)
    summer_months = [4, 5, 6, 7, 8, 9, 10]
    summer_all = df[df["month"].isin(summer_months)]["USAGE"].sum()

    # 4. All values
    total_usage = df["USAGE"].sum()

    # Convert Wh to kWh if the units are in Wh
    conversion = 1000 if "Wh" in df["UNITS"].iloc[0] else 1

    # Convert all values to kWh
    winter_peak_kwh = winter_peak / conversion
    winter_off_peak_kwh = winter_off_peak / conversion
    summer_kwh = summer_all / conversion
    total_kwh = total_usage / conversion

    # Calculate costs for time-of-use billing
    winter_peak_cost = winter_peak_kwh * RATE_WINTER_PEAK
    winter_off_peak_cost = winter_off_peak_kwh * RATE_WINTER_OFF_PEAK
    summer_cost = summer_kwh * RATE_SUMMER
    total_time_of_use_cost = winter_peak_cost + winter_off_peak_cost + summer_cost

    # Calculate cost for fixed rate
    total_fixed_rate_cost = total_kwh * RATE_FIXED

    # Calculate the savings (positive means time-of-use is cheaper)
    savings = total_fixed_rate_cost - total_time_of_use_cost

    results = {
        "winter_peak_usage": winter_peak_kwh,
        "winter_off_peak_usage": winter_off_peak_kwh,
        "summer_usage": summer_kwh,
        "total_usage": total_kwh,
        "winter_peak_percentage": (winter_peak / total_usage * 100),
        "winter_off_peak_percentage": (winter_off_peak / total_usage * 100),
        "summer_percentage": (summer_all / total_usage * 100),
        # Cost analysis
        "winter_peak_cost": winter_peak_cost,
        "winter_off_peak_cost": winter_off_peak_cost,
        "summer_cost": summer_cost,
        "total_time_of_use_cost": total_time_of_use_cost,
        "total_fixed_rate_cost": total_fixed_rate_cost,
        "savings": savings,
    }

    # Extract metadata
    metadata = {}
    with open(file_path, "r") as file:
        for _ in range(header_row):
            line = file.readline().strip()
            if "," in line:
                key, value = line.split(",", 1)
                metadata[key] = value

    results["metadata"] = metadata
    return results


def format_results(results):
    """Format the results for display"""
    # First display metadata if available
    if "metadata" in results:
        print("\nAccount Information:")
        print("-" * 60)
        metadata = results["metadata"]
        if "Name" in metadata:
            print(f"Name: {metadata['Name']}")
        if "Address" in metadata:
            print(f"Address: {metadata['Address']}")
        if "Account Number" in metadata:
            print(f"Account Number: {metadata['Account Number']}")

    print("\nPower Usage Analysis Results:")
    print("-" * 60)
    print("Usage Breakdown:")
    print(
        f"Winter Peak Hours (Nov-Mar, 7-11 & 17-21): {results['winter_peak_usage']:.2f} kWh ({results['winter_peak_percentage']:.1f}%)"
    )
    print(
        f"Winter Off-Peak Hours (Nov-Mar, other times): {results['winter_off_peak_usage']:.2f} kWh ({results['winter_off_peak_percentage']:.1f}%)"
    )
    print(
        f"Summer Usage (Apr-Oct, all hours): {results['summer_usage']:.2f} kWh ({results['summer_percentage']:.1f}%)"
    )
    print(f"Total Usage: {results['total_usage']:.2f} kWh")

    print("\nCost Analysis:")
    print("-" * 60)
    print("Time-of-Use Rate Breakdown:")
    print(
        f"Winter Peak Hours (${RATE_WINTER_PEAK:.5f}/kWh): ${results['winter_peak_cost']:.2f}"
    )
    print(
        f"Winter Off-Peak Hours (${RATE_WINTER_OFF_PEAK:.5f}/kWh): ${results['winter_off_peak_cost']:.2f}"
    )
    print(f"Summer Usage (${RATE_SUMMER:.5f}/kWh): ${results['summer_cost']:.2f}")
    print(f"Total Time-of-Use Cost: ${results['total_time_of_use_cost']:.2f}")

    print(
        f"\nFixed Rate Cost (${RATE_FIXED:.5f}/kWh): ${results['total_fixed_rate_cost']:.2f}"
    )

    savings = results["savings"]
    if savings > 0:
        print(f"\nTime-of-Use billing would save you: ${abs(savings):.2f}")
    else:
        print(f"\nFixed rate billing would save you: ${abs(savings):.2f}")


def main():
    parser = argparse.ArgumentParser(description="Analyze power usage from CSV file.")
    parser.add_argument("file_path", help="Path to the CSV file")
    args = parser.parse_args()

    try:
        results = analyze_power_usage(args.file_path)
        format_results(results)
    except Exception as e:
        print(f"Error processing file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    main()
