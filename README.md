
# GND ID Search

This Python program is designed to find GND (Gemeinsame Normdatei) IDs for people based on their names, professions, and birth years. The program fetches data from the GND API and matches people with their respective GND IDs.

## Features

- Fetches GND IDs for people based on a table and adds them.
- Handles retries and errors while making requests to the GND API.
- Supports logging for debugging and tracking the program's execution.
- Uses an external configuration file (`settings.ini`) for customizable settings.
- Includes logic to handle existing GND IDs and merge them with found IDs.

## Prerequisites

- Python 3.x
- Required Python packages: `pandas`, `requests`, `tqdm`, `configparser`, `python-dateutil`

## Installation

1. Clone this repository or download the script files.

2. Install the required Python packages using pip:
    ```bash
    pip install pandas requests tqdm python-dateutil
    ```

3. Make sure you have the following files in the same directory:
    - `gnd_id_search.py`
    - `settings.ini`

## Configuration

The `settings.ini` file is used to configure the program. It includes the base URL for the GND API and the list of professions seperated by "," to filter by. Please make sure to include all possible variants of your choosen profession.

Example `settings.ini`:
```ini
[DEFAULT]
BaseURL = https://lobid.org/gnd/search?q=
Profession = Komponist,Komponistin 

[LOGGING]
LogFileName = gnd_finder.log
LogLevel = INFO
LogFormat = %(asctime)s - %(levelname)s - %(message)s
```

## Usage

1. Import the necessary functions from the script:
    ```python
    from gnd_id_finder_mod import add_gnd_id, read_config
    ```

2. Load your data into a pandas DataFrame:
    ```python
    import pandas as pd
    df = pd.read_csv('your_data.csv')
    ```

3. Add GND IDs to your DataFrame:
    ```python
    updated_df = add_gnd_id(df)
    ```

4. Save the updated DataFrame to a file of your choice:
    ```python
    updated_df.to_csv('updated_data.csv', index=False)
    ```



## Sample Input DataFrame

The input DataFrame should have the following columns: `first_name`, `last_name`, `birth_year`.

Example:
```python
import pandas as pd

data = {
    'first_name': ['Ludwig', 'Wolfgang', 'Johann'],
    'last_name': ['van Beethoven', 'Amadeus Mozart', 'Sebastian Bach'],
    'birth_year': [1770, 1756, 1685]
}

df = pd.DataFrame(data)
print(df)
```

This will create a DataFrame that looks like this:

| first_name | last_name        | birth_year |
|------------|------------------|------------|
| Ludwig     | van Beethoven    | 1770       |
| Wolfgang   | Amadeus Mozart   | 1756       |
| Johann     | Sebastian Bach   | 1685       |

## Output

The output will be a pandas DataFrame with two additional columns: `gnd_id_search` and `possible_gnd_ids`.

- `gnd_id_search`: Contains the found GND IDs for the composer. If it is more than one GND_ID and matches birth_year , first_name and last_name multiple GND_IDs are written in that column.  

- `possible_gnd_ids`: Contains possible GND IDs if no exact match was found.

Example output DataFrame:

| first_name | last_name        | birth_year | gnd_id_search | possible_gnd_ids |
|------------|------------------|------------|---------------|------------------|
| Ludwig     | van Beethoven    | 1770       | 1234567       |                  |
| Wolfgang   | Amadeus Mozart   | 1756       | 2345678       |                  |
| Johann     | Sebastian Bach   | 1685       |               | 3456789, 4567890 |

## What if my data includes GND IDs partially?

You can use this tool to find more GND IDs, but it is recommended to prioritize the GND ID in your initial data. The program includes logic to check if the provided GND ID is the same or valid. Your original data should include a column named `gnd_id` if you want to merge the found IDs with the provided ones. To use this feature, simply add `resolve_ids=True`.

The logic works as follows:
- Strips whitespace from the `gnd_id`, `gnd_id_search`, and `possible_gnd_ids` columns.
- If `gnd_id` is `None` or its length is less than 9 (length of a valid GND ID), it replaces `gnd_id` with `gnd_id_search`.
- If `gnd_id_search` and `gnd_id` contain the same ID, it keeps `gnd_id`.
- If `gnd_id` and `possible_gnd_ids` contain the same ID, it clears `possible_gnd_ids`.
- If `gnd_id` is empty but `gnd_id_search` is not, it sets `gnd_id` to `gnd_id_search`.
- If `gnd_id` is not empty, it clears `possible_gnd_ids`. 

Example:

```python
updated_df = add_gnd_id(df,resolve_ids=True)
```

## Logging

The program uses logging to track its execution. The logging configuration is specified in the `settings.ini` file. By default, logs are written to `gnd_id_search.log` with the `INFO` level and a specific format.

## License

This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.

## Acknowledgements

This program uses the GND API provided by the German National Library. For more information, visit [GND API documentation](https://lobid.org/gnd/api).
```
This `README.md` includes all the necessary details about the program, its configuration, usage, and a sample input DataFrame. Let me know if there's anything else you need!