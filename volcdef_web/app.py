from flask import Flask, render_template, jsonify, abort
import json
import os

app = Flask(__name__)
# Read Mapbox access token from environment variable
APP_DIR = os.path.dirname(__file__)

TOKEN_FILE = os.path.join( os.path.dirname(APP_DIR), "mapbox_access_token.env")

def load_mapbox_token():

    namespace = {}
    with open(TOKEN_FILE, "r") as f:
        exec(f.read(), namespace)
    token = namespace.get("mapbox_access_token", "").strip()

    if not token or "YourTokenHere" in token:
        raise RuntimeError( "MAPBOX access token not set (still placeholder)")

    return token

MAPBOX_ACCESS_TOKEN = load_mapbox_token()

VOLCDEF_WEB_HOME = os.getenv('VOLCDEF_WEB_HOME', os.path.dirname(__file__))

# Find volcanoes JSON file: $MINSAR_HOME/webconfig or local data directory
def get_volcanoes_json_path():
    minsar_home = os.getenv('MINSAR_HOME')
    if minsar_home:
        minsar_json = os.path.join(minsar_home, 'webconfig', 'volcanoes_volcdef.json')
        if os.path.exists(minsar_json):
            return minsar_json
    return os.path.join(VOLCDEF_WEB_HOME, 'data', 'volcanoes_volcdef.json')

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=MAPBOX_ACCESS_TOKEN)

# Load volcano data from determined path
volcanoes_json_path = get_volcanoes_json_path()
with open(volcanoes_json_path) as f:
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
