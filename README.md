# Volcano deformation
Flask based website to display University of Miami geodesylab volcano displacement timeseries data.

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
   The app reads `volcanoes.json` (the volcano list) from (in this order): **sibling webconfig** (same parent dir as VolcDef_web) ,  `WEBCONFIG_DIR/volcanoes.json` (if set),  `volcdef_web/data/volcanoes.json` or `volcanoes_volcdef.json`. Paths are relative; no `MINSAR_HOME` is required.  
   In production, set `WEBCONFIG_DIR` to the webconfig directory (e.g. `/var/www/webconfig`) so a single shared config is used (`volcdef_web.conf` sets `SetEnv WEBCONFIG_DIR /var/www/webconfig`).  
   To update the volcano list, go to `/var/www/webconfig` and run `make_volcdef_volcanoes_json.py` (without arguments). it reads Holocene*.xlsx and writes `volcanoes.json` into the current directory (alternatively: `make_volcdef_volcanoes_json.py /path/to/Holocene_Volcanoes_volcdef_cfg.xlsx --outdir /var/www/webconfig`)

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




