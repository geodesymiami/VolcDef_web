from flask import Flask, render_template, jsonify, abort
import json
import os

app = Flask(__name__)


def _is_landslide(entry):
    """True if this record is a landslide case (sorted last on list/map).

    Primary rule: Holocene / volcanoes.json uses ``type`` from Excel column
    ``Primary Volcano Type``; landslide entries are labeled ``Landslide`` there.
    Optional explicit ``Landslide`` boolean in JSON still supported.
    """
    ptype = entry.get("type") or entry.get("Primary Volcano Type")
    if ptype is not None and not (isinstance(ptype, float) and ptype != ptype):  # not NaN
        if str(ptype).strip().lower() == "landslide":
            return True

    val = entry.get("Landslide")
    if val is None:
        val = entry.get("landslide")
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    s = str(val).strip().lower()
    return s in ("true", "yes", "1", "y")


def _sort_volcanoes_for_display(volcanoes):
    """Non-landslides first (by name), then landslides (by name)."""
    return sorted(
        volcanoes,
        key=lambda v: (_is_landslide(v), str(v.get("name") or "").lower()),
    )
# Read Mapbox access token from environment variable
APP_DIR = os.path.dirname(__file__)

TOKEN_FILE = os.path.join( os.path.dirname(APP_DIR), "mapbox_access_token.env")
print("TOKEN_FILE:",TOKEN_FILE)

def load_mapbox_token():

    namespace = {}
    with open(TOKEN_FILE, "r") as f:
        exec(f.read(), namespace)
    token = namespace.get("mapbox_access_token", "").strip()
    print("token:",token)

    if not token or "YourTokenHere" in token:
        raise RuntimeError( "MAPBOX access token not set (still placeholder)")

    return token

MAPBOX_ACCESS_TOKEN = load_mapbox_token()

VOLCDEF_WEB_HOME = os.getenv('VOLCDEF_WEB_HOME', os.path.dirname(__file__))

# Find volcanoes.json: sibling webconfig (same parent as VolcDef_web), then WEBCONFIG_DIR, then bundled data
def get_volcanoes_json_path():
    # Sibling webconfig dir (webconfig and VolcDef_web share the same parent)
    parent_of_volcdef = os.path.dirname(APP_DIR)
    shared_parent = os.path.dirname(parent_of_volcdef)
    sibling_webconfig = os.path.join(shared_parent, 'webconfig')
    sibling_json = os.path.join(sibling_webconfig, 'volcanoes.json')
    if os.path.exists(sibling_json):
        return sibling_json
    webconfig_dir = os.getenv('WEBCONFIG_DIR')
    if webconfig_dir:
        path = os.path.join(webconfig_dir, 'volcanoes.json')
        if os.path.exists(path):
            return path
    # Bundled data: volcanoes.json or fallback to volcanoes_volcdef.json
    bundled = os.path.join(VOLCDEF_WEB_HOME, 'data', 'volcanoes.json')
    if os.path.exists(bundled):
        return bundled
    return os.path.join(VOLCDEF_WEB_HOME, 'data', 'volcanoes_volcdef.json')

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=MAPBOX_ACCESS_TOKEN)

# Load volcano data from determined path
volcanoes_json_path = get_volcanoes_json_path()
with open(volcanoes_json_path) as f:
    volcanoes = _sort_volcanoes_for_display(json.load(f)["volcanoes"])

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
