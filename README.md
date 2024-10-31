# Nova Scotia Power Time-of-Use Calculator

## Overview

This script is designed to help calculate a household's costs/savings from signing up for the [Time-of-Use pilot program from NSPower](https://www.nspower.ca/your-home/residential-rates/time-of-use).

## Installation

To install the NSPower TOU Calculator, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/KenMacD/nspower-tou-calc.git
    ```

2. Navigate to the project directory:

    ```bash
    cd nspower-tou-calc
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use the NSPower TOU Calculator, follow these steps:

1. Log in to [myaccount.nspower.ca](https://myaccount.nspower.ca/)
2. Click "MyEnergy Insights"
3. In the upper-right menu click "Download my data"
4. Export the data for an entire year in `.csv` format
5. Run `python power-usage-analysis.py <CSV_FILE>`

If you have `uv` installed then the script can be run with `uv run power-usage-analysis.py` without even pre-installing the dependencies.

## Output

The output for the script should look like:

```text
Account Information:
------------------------------------------------------------
Name: JOHN DOE
Address: 1234 MAIN STREET
Account Number: 1234567

Power Usage Analysis Results:
------------------------------------------------------------
Usage Breakdown:
Winter Peak Hours (Nov-Mar, 7-11 & 17-21): 872.25 kWh (11.0%)
Winter Off-Peak Hours (Nov-Mar, other times): 1884.54 kWh (23.7%)
Summer Usage (Apr-Oct, all hours): 5184.40 kWh (65.3%)
Total Usage: 7941.18 kWh

Cost Analysis:
------------------------------------------------------------
Time-of-Use Rate Breakdown:
Winter Peak Hours ($0.34634/kWh): $302.10
Winter Off-Peak Hours ($0.17703/kWh): $333.62
Summer Usage ($0.12198/kWh): $632.39
Total Time-of-Use Cost: $1268.11

Fixed Rate Cost ($0.17703/kWh): $1405.83

Time-of-Use billing would save you: $137.72

```
