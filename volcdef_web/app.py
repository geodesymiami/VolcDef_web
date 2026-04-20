from flask import Flask, render_template, jsonify, abort
import json
import os
import sys

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

# Primary data file name for VolcDef web (Holocene list + volcdef fields).
_VOLCDEF_JSON = 'volcanoes_volcdef.json'


def get_volcanoes_json_path():
    """Resolve path to volcano JSON.

    1. Production: /var/www/webconfig/volcanoes_volcdef.json
    2. Dev / repo layout: realpath(../webconfig/volcanoes_volcdef.json) relative to the VolcDef_web
       install root (parent of ``volcdef_web/``), e.g.
       .../minsar/tools/webconfig/volcanoes_volcdef.json when VolcDef_web lives under .../tools/VolcDef_web.
    3. $WEBCONFIG_DIR/volcanoes_volcdef.json if set.
    4. Bundled data under this package.
    """
    prod = os.path.join('/var/www/webconfig', _VOLCDEF_JSON)
    if os.path.isfile(prod):
        return prod

    # VolcDef_web repo root = directory that contains volcdef_web/ (e.g. .../VolcDef_web)
    volcdef_web_root = os.path.dirname(APP_DIR)
    # ../webconfig/volcanoes_volcdef.json from that root (sibling webconfig next to VolcDef_web)
    sibling_volcdef = os.path.join(
        os.path.dirname(volcdef_web_root), 'webconfig', _VOLCDEF_JSON
    )
    sibling_resolved = os.path.realpath(sibling_volcdef)
    if os.path.isfile(sibling_resolved):
        return sibling_resolved

    webconfig_dir = os.getenv('WEBCONFIG_DIR')
    if webconfig_dir:
        path = os.path.join(webconfig_dir, _VOLCDEF_JSON)
        if os.path.isfile(path):
            return path
        path_json = os.path.join(webconfig_dir, 'volcanoes.json')
        if os.path.isfile(path_json):
            return path_json

    bundled = os.path.join(VOLCDEF_WEB_HOME, 'data', 'volcanoes.json')
    if os.path.isfile(bundled):
        return bundled
    return os.path.join(VOLCDEF_WEB_HOME, 'data', _VOLCDEF_JSON)


def _is_bundled_sample_path(path):
    """True if path is the small packaged data/volcanoes_volcdef.json (not /var/www/webconfig)."""
    try:
        return os.path.samefile(
            path,
            os.path.join(VOLCDEF_WEB_HOME, 'data', _VOLCDEF_JSON),
        )
    except OSError:
        return False

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=MAPBOX_ACCESS_TOKEN)

# Load volcano data from determined path (at import time; restart WSGI after editing JSON)
volcanoes_json_path = os.path.abspath(get_volcanoes_json_path())
with open(volcanoes_json_path) as f:
    volcanoes = _sort_volcanoes_for_display(json.load(f)["volcanoes"])

VOLCANOES_COUNT = len(volcanoes)
_msg = (
    f"[VolcDef_web] Loaded {VOLCANOES_COUNT} volcanoes from {volcanoes_json_path}"
)
print(_msg, file=sys.stderr)

_webconfig = os.getenv("WEBCONFIG_DIR")
if _webconfig and _is_bundled_sample_path(volcanoes_json_path):
    _expected = os.path.join(_webconfig, _VOLCDEF_JSON)
    print(
        "[VolcDef_web] WARNING: WEBCONFIG_DIR is set but the bundled sample "
        f"({VOLCANOES_COUNT} entries) is being used. Deploy and chmod "
        f"so the WSGI user can read: {_expected}",
        file=sys.stderr,
    )

@app.route('/api/data_source')
def data_source():
    """Ops: which JSON file the app loaded and how many volcanoes (verify vs /var/www/webconfig)."""
    return jsonify(
        {
            "volcanoes_json_path": volcanoes_json_path,
            "volcanoes_count": VOLCANOES_COUNT,
            "webconfig_dir": os.getenv("WEBCONFIG_DIR"),
            "using_bundled_sample": _is_bundled_sample_path(volcanoes_json_path),
        }
    )

@app.route('/api/volcanoes')
def get_volcanoes():
    return jsonify(volcanoes)

@app.route('/volcanoes')
def volcanoes_list():
    """Volcanoes first, then a separate block for landslides (see _is_landslide)."""
    volcanoes_only = [v for v in volcanoes if not _is_landslide(v)]
    landslides_only = [v for v in volcanoes if _is_landslide(v)]
    return render_template(
        'volcanoes_list.html',
        volcanoes=volcanoes_only,
        landslides=landslides_only,
    )

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
