import pandas as pd
import requests
import logging
from tqdm import tqdm
import configparser
from requests.exceptions import RequestException
import time
from dateutil import parser as date_parser

def read_config(filename='settings.ini'):
    try:
        config = configparser.ConfigParser(interpolation=None)
        config.read(filename)
        return config
    
    except Exception as e:
        logging.error(f'An error occurred while reading the configuration file: {e}')
        return None


def resolve_gnd_id(combined_df):
    
    combined_df.fillna({'gnd_id': '', 'gnd_id_search': '', 'possible_gnd_ids': ''}, inplace=True)

    for index, row in combined_df.iterrows():
            
            row['gnd_id'].strip()
            row['gnd_id_search'].strip()
            row['possible_gnd_ids'].strip()
            
            if row['gnd_id'] == None:
                pass
            elif len(row['gnd_id']) < 9:
                combined_df.at[index, 'gnd_id'] = row['gnd_id_search']
        
            same_id_check_gnd_finder = set(row['gnd_id_search']).add(row['gnd_id'])
            if same_id_check_gnd_finder == None:
                pass
            elif len(same_id_check_gnd_finder) == 1:
                combined_df.at[index, 'gnd_id'] = same_id_check_gnd_finder
        
            same_id_check_possible_gnd = set(row['gnd_id']).add(row['possible_gnd_ids'])
            if same_id_check_possible_gnd == None:
                pass
            elif len(same_id_check_possible_gnd) == 1:
                combined_df.at[index, 'possible_gnd_ids'] = ''
        
            if row['gnd_id'] == '' and row['gnd_id_search'] != '':
                combined_df.at[index, 'gnd_id'] = row['gnd_id_search']

            if row['gnd_id'] != '' :
                combined_df.at[index, 'possible_gnd_ids'] = ''

    logging.info('gnd_id resolved')
    return combined_df

def gnd_id_finder(composer_name, professions, base_url, session, max_retries=3):
    gnd_ids = []

    # Replace spaces with '+' for URL
    composer_name = composer_name.replace(' ', '+')
    url = base_url + composer_name

    retries = 0
    while retries < max_retries:
        try:
            response = session.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['totalItems'] > 0:
                    for item in data['member']:
                        if 'professionOrOccupation' in item:
                            for profession in item['professionOrOccupation']:
                                if profession['label'] in professions:
                                    gnd_ids.append(item['gndIdentifier'])
                break
            else:
                logging.error(f'Failed to fetch data from GND API for query: {composer_name}. Status code: {response.status_code}')
        except RequestException as e:
            logging.exception(f'An error occurred for query {composer_name}: {e}')
        retries += 1
        time.sleep(1)  # Adding a delay before retrying

    if retries == max_retries:
        logging.error(f'Failed to fetch data from GND API for query: {composer_name} after {max_retries} attempts.')

    return gnd_ids

def fetch_possible_gnd_ids(composer_name, primary_gnd_id, base_url, session, max_retries=3):
    possible_ids = []
    composer_name = composer_name.replace(' ', '+')
    url = base_url + composer_name

    retries = 0
    while retries < max_retries:
        try:
            response = session.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['totalItems'] > 0:
                    for item in data['member']:
                        if item['gndIdentifier'] and item['gndIdentifier'] != primary_gnd_id:
                            possible_ids.append(item['gndIdentifier'])
                break
            else:
                logging.error(f'Failed to fetch data for possible GND IDs for query: {composer_name}. Status code: {response.status_code}')
        except RequestException as e:
            logging.exception(f'An error occurred while fetching possible GND IDs for query {composer_name}: {e}')
        retries += 1
        time.sleep(1)  # Adding a delay before retrying

    if retries == max_retries:
        logging.error(f'Failed to fetch data for possible GND IDs for query: {composer_name} after {max_retries} attempts.')

    return possible_ids

def add_gnd_id(dataframe: pd.DataFrame, resolve_ids=False) -> pd.DataFrame:
    config = read_config()
    base_url = config['DEFAULT']['BaseURL']
    professions = config['DEFAULT']['Profession'].split(',')
    log_file = config['LOGGING']['LogFileName']
    log_format = config['LOGGING']['LogFormat']
    log_level = config['LOGGING']['LogLevel']

    # Setup logging
    logging.basicConfig(filename=log_file, level=log_level, format=log_format)

    dataframe['gnd_id_search'] = ''  # Initialize column for GND IDs
    dataframe['possible_gnd_ids'] = ''  # Initialize column for possible GND IDs

    nothing_found = True

    with requests.Session() as session:
        for index, row in tqdm(dataframe.iterrows(), total=dataframe.shape[0], desc='Finding GND IDs'):
            query = f"{str(row['first_name']).strip()} {str(row['last_name']).strip()}"
            gnd_id = []

            if not pd.isna(row['birth_year']):
                try:
                    birth_year = date_parser.parse(str(row['birth_year'])).year
                except ValueError:
                    birth_year = row['birth_year']
                    logging.warning(f'Invalid birth year for query: {query}. Using the provided year as is.')

                query_birth_year = f"{query} {str(birth_year)}"
                gnd_id = gnd_id_finder(query_birth_year, professions, base_url, session)
            
            if not gnd_id:
                gnd_id = gnd_id_finder(query, professions, base_url, session)
            
            gnd_id = list(set(gnd_id))

            if gnd_id:
                dataframe.at[index, 'gnd_id_search'] = ', '.join(gnd_id)
                nothing_found = False
            else:
                possible_ids = fetch_possible_gnd_ids(query, None, base_url, session)
                dataframe.at[index, 'possible_gnd_ids'] = ', '.join(possible_ids)
                logging.info(f'No GND IDs found for query: {query}')

    if nothing_found:
        logging.warning('No GND IDs found for any entry.')

    if resolve_ids:
        dataframe = resolve_gnd_id(dataframe)

    return dataframe