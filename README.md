# Volcano deformation
Flask based website to display University of Miami geodesylab volcano displacement timeseries data.

## Repository copy vs production on the server

| Location | Role |
|----------|------|
| **`$MINSAR_HOME/tools/VolcDef_web`** (this repo) | Where you edit code in development (e.g. under `minsar/tools/VolcDef_web`). |
| **`/var/www/VolcDef_web`** | **What Apache/WSGI actually runs** (`web.wsgi`, `volcdef_web/app.py`, `web_env`). |

Changes made in the MinSAR repo are **not** live until you **deploy** them to `/var/www/VolcDef_web`, for example:

```bash
# Example: sync Python package (adjust host/user as needed)
sudo rsync -a --delete /path/to/minsar/tools/VolcDef_web/volcdef_web/ /var/www/VolcDef_web/volcdef_web/
sudo systemctl reload apache2
```

Or maintain `/var/www/VolcDef_web` as a `git clone` / `git pull` of [VolcDef_web](https://github.com/geodesymiami/VolcDef_web) and pull on the server after merging changes from the minsar copy.
c## Installation
1. Go to `/var/www/` and clone the repository (on a new server you may need your private and public key in ~/.ssh for git to work)
```
git clone git@github.com:geodesymiami/VolcDef_web
git clone git@github.com:geodesymiami/webconfig
```
(preferred), or if cloned into the $MINSAR_HOME/tools directory create a symbolic link:
```
sudo ln -s /home/exouser/code/minsar/tools/VolcDef_web /var/www
```
2. Install the required packages into a virtual environment (first adjust ownership:
```
USER=insaradmin
szdo chown -R $USER:$USER /var/www/VolcDef_web

python -m venv web_env
source web_env/bin/activate
pip install -r requirements.txt
```
3. Make sure the MAPBOX_ACCESS_TOKEN is set in `mapbox_access_token.env` (or `cp ~/accounts/mapbox_access_token.env .`).

4. **Volcano list (production)**  
   The app uses **`/var/www/webconfig/volcanoes_volcdef.json`**, then sibling `../webconfig/volcanoes_volcdef.json`, then `WEBCONFIG_DIR/volcanoes_volcdef.json`. See `volcdef_web/app.py` (`get_volcanoes_json_path`).  `SetEnv WEBCONFIG_DIR /var/www/webconfig` is set in`volcdef_web.conf`.

6. Run the website
```
cd volcdef_web/
python run.py
```
6. Check whether website is running using
```
curl -s http://127.0.0.1:5001
```
or  open website at the given address (chrome/safari)
```
127.0.0.1:5001
```
7. On a remote server, to configure Apache copy volcdef_web.conf to /etc/apache2/sites-available/ (`sudo cp volcdef_web.conf /etc/apache2/sites-available/`)((Ubuntu, `/etc/httpd/conf.d` for Alma/RedHat) (use `volcdef_web.conf_jetstream` is /data/HDFEOS5 lives on server running Apache). 

8. Start Apache using:
```
sudo a2ensite volcdef_web.conf
sudo systemctl restart apache2
```
8. Check for errors using:
```
sudo tail -20 /var/log/apache2/error.log
```
If you see a Traceback, then python could not properly run your `web.wsgi` or `app.py`.


 ## Update voclano list  
   To update the volcano list on theserver, go to `/var/www/webconfig` and update using `git pull`. Else, run `make_volcdef_volcanoes_json.py` with `--outdir /var/www/webconfig` (or from that directory). Reload Apache after updating the JSON so WSGI reloads (`sudo systemctl restart apache2`)e; JSON alone may require a process reload depending on setup.


