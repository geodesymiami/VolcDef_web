#! /usr/bin/env python
# convert excel file to json
import os
import argparse
import pandas as pd
import json

def main():
    parser = argparse.ArgumentParser(
        description='Creates a volcanoes.json file for the VolcDef website based on a Holocene_volcanoes.xls file.'
    )
    
    # Get the default path: one directory up from the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_file = os.path.join(os.path.dirname(script_dir), 'Holocene_Volcanoes_volcdef_cfg.xlsx')
    
    parser.add_argument(
        'input_file',
        nargs='?',
        default=default_file,
        help='Path to the Holocene_volcanoes Excel file (default: VolcDef_web/Holocene_Volcanoes_volcdef_cfg.xlsx)'
    )
    
    args = parser.parse_args()
    
    FILE_PATH = args.input_file
    print(f'Reading {FILE_PATH} ...')
    df = pd.read_excel(FILE_PATH, skiprows=1)

    # Process the DataFrame to create a list of volcano dictionaries
    volcanoes = []
    for _, row in df.iterrows():
        # Clean the VolcDef link by removing leading/trailing whitespace including non-breaking spaces
        volcdef_link = row['VolcDef']
        if isinstance(volcdef_link, str):
            volcdef_link = volcdef_link.strip().replace('\u00a0', '')
        
        volcano = {
            'id': row['Volcano Number'],
            'name': row['Volcano Name'],
            'country': row['Country'],
            'type': row['Primary Volcano Type'],
            'activity_evidence': row['Activity Evidence'],
            'last_known_eruption': row['Last Known Eruption'],
            'region': row['Region'],
            'subregion': row['Subregion'],
            'latitude': row['Latitude'],
            'longitude': row['Longitude'],
            'elevation': row['Elevation (m)'],
            'dominant_rock_type': row['Dominant Rock Type'],
            'tectonic_setting': row['Tectonic Setting'],
            'volcdef_link': volcdef_link
        }
        volcanoes.append(volcano)

    print(df['VolcDef'].value_counts())

    print('# of volcanoes:', len(volcanoes))
    # remove volcanoes with precip != False
    volcanoes = [volcano for volcano in volcanoes if volcano['volcdef_link'] != False]
    print('# of volcanoes with VolcDef:', len(volcanoes))
    # Create the final JSON structure
    volcano_data = {
        'volcanoes': volcanoes
    }


    print()
    print(volcanoes[0])


    # fix name if it has a comma
    for volcano in volcanoes:
        name = volcano['name']
        if ',' in name:
            name = name.split(',')[::-1]
            name = [part.strip() for part in name]
            volcano['name'] = ' '.join(name)

    # Handle duplicate volcano entries
    # Track how many times we've seen each volcano name
    volcano_name_count = {}
    
    for volcano in volcanoes:
        name = volcano['name']
        
        # Check if this is a duplicate
        if name in volcano_name_count:
            # This is the second (or later) occurrence
            # Subtract 0.001 from latitude to offset the marker
            volcano['latitude'] -= 0.001
            
            # Extract processing method from URL (miaplpy or mintpy)
            url = volcano['volcdef_link']
            if 'miaplpy' in url:
                volcano['name'] = f"{name} (miaplpy)"
            elif 'mintpy' in url:
                volcano['name'] = f"{name} (mintpy)"
            
            print(f"Duplicate found: {name} -> {volcano['name']}, adjusted latitude to {volcano['latitude']}")
        
        # Increment the count for this volcano name
        volcano_name_count[name] = volcano_name_count.get(name, 0) + 1

    # move the json file to the data directory
    # Write the JSON data to a file
    json_file = 'data/volcanoes.json'
    with open(json_file, 'w') as json_file:
        json.dump(volcano_data, json_file, indent=4)

    print(f'JSON file created: {json_file}')


if __name__ == '__main__':
    main()

