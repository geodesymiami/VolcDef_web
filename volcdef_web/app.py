from flask import Flask, render_template, jsonify, abort
import json
import os

app = Flask(__name__)
# Read Mapbox access token from environment variable
APP_DIR = os.path.dirname(__file__)

PRIMARY_TOKEN_FILE = os.path.expanduser( "~/accounts/mapbox_access_token.env")
FALLBACK_TOKEN_FILE = os.path.join( os.path.dirname(APP_DIR), "mapbox_access_token.env")

def load_mapbox_token():
    if os.path.exists(PRIMARY_TOKEN_FILE):
        token_file = PRIMARY_TOKEN_FILE
    else:
        token_file = FALLBACK_TOKEN_FILE

    namespace = {}
    with open(token_file, "r") as f:
        exec(f.read(), namespace)
    token = namespace.get("mapbox_access_token", "").strip()

    if not token or "YourTokenHere" in token:
        raise RuntimeError( "MAPBOX access token not set (still placeholder)")

    return token

MAPBOX_ACCESS_TOKEN = load_mapbox_token()

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
