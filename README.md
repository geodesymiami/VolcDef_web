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

## Installation
1. Go to `/var/www/` and clone the repository:
```
git clone git@github.com:geodesymiami/VolcDef_web
```
(preferred), or if cloned into the $MINSAR_HOME/tools directory create a symbilic link:
```
sudo ln -s /home/exouser/code/minsar/tools/VolcDef_web /var/www
```
2. In the VolcDef_web dir, install the required packages into a virtual environment:
```
python -m venv web_env
source web_env/bin/activate
pip install -r requirements.txt
```
3. Make sure the MAPBOX_ACCESS_TOKEN is set in `mapbox_access_token.env` (or `cp ~/accounts/mapbox_access_token.env .`).

4. **Volcano list (production)**  
   The app prefers **`/var/www/webconfig/volcanoes_volcdef.json`**, then sibling `../webconfig/volcanoes_volcdef.json`, then `WEBCONFIG_DIR/volcanoes_volcdef.json` and `volcanoes.json`, then bundled `data/`. See `volcdef_web/app.py` (`get_volcanoes_json_path`).  
   In production, `volcdef_web.conf` sets `SetEnv WEBCONFIG_DIR /var/www/webconfig`.  
   To update the volcano list, run `make_volcdef_volcanoes_json.py` with `--outdir /var/www/webconfig` (or from that directory). Reload Apache after updating the JSON so WSGI reloads if you change code; JSON alone may require a process reload depending on setup.

5. Run the website
```
cd volcdef_web/
python run.py
```
6. Open Website at the given address (chrome/safari)
```
127.0.0.1:5000
```
or check using
```
curl -s http://127.0.0.1:5000
```
7. On a remote server, to configure Apache copy volcdef_web.conf to /etc/apache2/sites-available/ (`sudo cp volcdef_web.conf /etc/apache2/sites-available/`. It contains
```
<VirtualHost *:80>

    # Alias directives must come BEFORE WSGIScriptAlias to prevent Flask from catching these URLs

    # Serve /data/HDF5EOS/ as static files (bypass WSGI/Flask)
    Alias /data/HDF5EOS/ /data/HDF5EOS/
    <Directory /data/HDF5EOS/>
        Options Indexes FollowSymLinks
        Require all granted
    </Directory>

    # Serve /data/precip_plots/ as static files
    Alias /data/precip_plots/ /data/precip_plots/
    <Directory /data/precip_plots/>
        Options Indexes FollowSymLinks
        Require all granted
    </Directory>

    # Flask/WSGI configuration (must come AFTER Alias directives)
    WSGIDaemonProcess precip_web python-home=/var/www/Precip_web/web_env python-path=/var/www/Precip_web
    WSGIProcessGroup precip_web
    WSGIScriptAlias / /var/www/Precip_web/web.wsgi

    <Directory /var/www/Precip_web/>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/precip_web_error.log
    CustomLog ${APACHE_LOG_DIR}/precip_web_access.log combined
</VirtualHost>
```

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




