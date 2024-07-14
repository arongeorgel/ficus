import json

import pandas as pd


def process_json(filename):
    """
    Reads a JSON file containing forex trade data, converts it to a pandas DataFrame,
    and creates entries for missing hours between existing data points.

    Args:
        filename: The path to the JSON file.

    Returns:
        A pandas DataFrame containing the processed data with missing hours filled.
    """
    data = []
    with open(filename, 'r') as f:
        for line in f:
            obj = json.loads(line.strip())
            data.append(obj)

    # Convert data to DataFrame and set "time" as index (assuming time is in datetime format)
    df = pd.DataFrame(data).set_index('time')

    # Upsample DataFrame to include all hours (assuming data is in UTC)
    df = df.resample('H', utc=True).fillna(method='ffill')  # Forward fill missing values

    return df


# Example usage (replace 'your_file.json' with the actual filename)
data_df = process_json('meta_symbol_btcusd_copy.json')


# Print the DataFrame (optional)
print(data_df)
