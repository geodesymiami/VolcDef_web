# Volcanic Deformation
Flask based website for displaying deformation.

## Installation
1. Go to `/var/www/` and clone the repository:
```
git clone git@github.com:geodesymiami/VolcDef_web
```
2. Install the required packages into an virtual environment:
```bash
python -m venv web_env
source web_env/bin/activate
pip install -r requirements.txt
```
3. Make sure the MAPBOX_ACCESS_TOKEN is set in `app.py` and the proper python version in `volcdef_web.wsgi`:
```bash
export MAPBOX_ACCESS_TOKEN=<your_mapbox_access_token>
site_packages = os.path.join(venv_path, 'lib/python3.12/site-packages')  # Replace python3.x with your Python version
```

4. Add the Flask app directory to the Python path
sys.path.insert(0, '/var/www/VolcDef_web/volcdef_web')
from volcdef_web import app
application = app
```
5. Run the website
```bash
cd volcdef_web/
python run.py
```
6. Open Website at the given address (chrome/safari)
```
127.0.0.1:5000
```
7. On a remote server, to configure Apache create `/etc/apache2/sites-available/volcdef_web.conf` containing
```
<VirtualHost *:80>
    ServerName 149.165.155.152

    WSGIDaemonProcess volcdef_web python-home=/var/www/VolcDef_web/web_env python-path=/var/www/VolcDef_web

    WSGIProcessGroup volcdef_web
    WSGIScriptAlias / /var/www/VolcDef_web/volcdef_web.wsgi

    <Directory /var/www/VolcDef_web/>
        Require all granted
    </Directory>

    # Map URL /data/precip_plots/ → filesystem /data/precip_plots/
    Alias /data/precip_plots/ /data/precip_plots/
    <Directory /data/precip_plots/>
        Options Indexes FollowSymLinks
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
If you see a Traceback, then python could not properly run your `volcdef_web.wsgi` or `app.py`.

