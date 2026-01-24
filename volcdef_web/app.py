from flask import Flask, render_template, jsonify, abort
import json
import os

app = Flask(__name__)
# Read Mapbox access token from environment variable

MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN','YourTokenHere')
PLOT_BASE_URL = 'http://149.165.155.152/data/precip_plots/'
VOLCDEF_WEB_HOME = os.getenv('VOLCDEF_WEB_HOME', os.path.dirname(__file__))

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=MAPBOX_ACCESS_TOKEN)

# Load volcano data
with open(f'{VOLCDEF_WEB_HOME}/data/volcanoes.json') as f:
    volcanoes = json.load(f)['volcanoes']


@app.route('/api/volcanoes')
def get_volcanoes():
    return jsonify(volcanoes)

@app.route('/volcanoes')
def volcanoes_list():
    # Assuming `get_volcanoes` is a function that retrieves all volcano data

    return render_template('volcanoes_list.html', volcanoes=volcanoes)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
