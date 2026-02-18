#! /usr/bin/env python
# convert excel file to json
import os
import argparse
import pandas as pd
import json

def main():
    parser = argparse.ArgumentParser(
        description='Creates volcanoes.json for the VolcDef website from Holocene_volcanoes xlsx. '
                    'Reads from sibling webconfig dir if present, else VolcDef_web repo. Writes to current directory by default.'
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Sibling of VolcDef_web (webconfig and VolcDef_web share the same parent)
    parent_of_volcdef = os.path.dirname(script_dir)
    shared_parent = os.path.dirname(parent_of_volcdef)
    sibling_webconfig = os.path.join(shared_parent, 'webconfig')

    # Default input: sibling webconfig/Holocene_Volcanoes_volcdef_cfg.xlsx if exists, else VolcDef_web repo
    sibling_xlsx = os.path.join(sibling_webconfig, 'Holocene_Volcanoes_volcdef_cfg.xlsx')
    if os.path.exists(sibling_xlsx):
        default_input = sibling_xlsx
    else:
        default_input = os.path.join(parent_of_volcdef, 'Holocene_Volcanoes_volcdef_cfg.xlsx')

    parser.add_argument(
        'input_file',
        nargs='?',
        default=default_input,
        help='Path to input Excel file (default: sibling webconfig/ or VolcDef_web/Holocene_Volcanoes_volcdef_cfg.xlsx)'
    )
    parser.add_argument(
        '--outdir',
        default='.',
        help='Output directory for volcanoes.json (default: current directory)'
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
            # Subtract 0.01 from latitude to offset the marker
            volcano['latitude'] -= 0.01

            # Extract processing method from URL (miaplpy or mintpy)
            url = volcano['volcdef_link']
            if 'miaplpy' in url:
                volcano['name'] = f"{name} (miaplpy)"
            elif 'mintpy' in url:
                volcano['name'] = f"{name} (mintpy)"

            print(f"Duplicate found: {name} -> {volcano['name']}, adjusted latitude to {volcano['latitude']}")

        # Increment the count for this volcano name
        volcano_name_count[name] = volcano_name_count.get(name, 0) + 1

    # Write JSON to output directory
    os.makedirs(args.outdir, exist_ok=True)
    json_file = os.path.join(args.outdir, 'volcanoes.json')
    with open(json_file, 'w') as f:
        json.dump(volcano_data, f, indent=4)

    print(f'JSON file created: {json_file}')


if __name__ == '__main__':
    main()

