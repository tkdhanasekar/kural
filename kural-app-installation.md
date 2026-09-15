## Installation of Kural app
create ssh key in new server and add in github account
```
apt update
```
```
apt install python3-pip python3-virtualenv nginx libpangocairo-1.0-0 certbot python3-certbot-nginx
```
clone the repo 
```
git clone git@github.com:tkdhanasekar/kural.git
```
```
mkdir code
```
```
mv kural/* code/
```
```
cd /root/code
```
```
rm -rf venv
```
```
apt install -y build-essential curl git libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
```
curl https://pyenv.run | bash
```
```
cat >> ~/.bashrc <<'EOF'
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
EOF
```
```
source ~/.bashrc
```
```
pyenv --version
```
```
pyenv install 3.8.20
```
```
cd /root/code
```
```
pyenv local 3.8.20
```
```
python --version
```
```
python -m venv venv38
```
```
source venv38/bin/activate
```
```
python -m pip install --upgrade "pip<24.1" setuptools
```
```
pip install -r /root/code/requirements.txt
```
```
pip install --upgrade pip
```
```
pip install Django==3.1.3 gunicorn
```
```
vim .env 
```
```
DB_HOST=127.0.0.1
DB_NAME=tirukkural
DB_USER=root
DB_PASS=Dashwood@321
APP_ENV=prod
TIME_ZONE=Asia/Kolkata
FROM_EMAIL=tamilttsweb@gmail.com
EMAIL_PASS=mypassword
SERVER_URL=https://xkural.hashlabs.in/
DEBUG=False
HOST=xkural.hashlabs.in
```
:wq!

run from terminal
```
export DB_HOST=127.0.0.1
export DB_NAME=tirukkural
export DB_USER=root
export DB_PASS=Dashwood@321
export APP_ENV=prod
export TIME_ZONE=Asia/Kolkata
export FROM_EMAIL=tamilttsweb@gmail.com
export EMAIL_PASS=mypassword
export SERVER_URL=https://xkural.hashlabs.in/
export DEBUG=False
export HOST=xkural.hashlabs.in
```
```
python manage.py check
```
```
gunicorn --bind 0.0.0.0:8000 tirukkuralweb.wsgi
```
check in browser xkural.hashlabs.in
ctrl+c
```
python manage.py collectstatic
```
yes
```
cd /etc/nginx/sites-enabled/
```
```
rm default
```
```
vim /etc/nginx/conf.d/kural.conf
```
```
server {
    listen 80;
    listen [::]:80;

    server_name xkural.hashlabs.in;

    location /userpdfs/ {
        alias /root/code/userpdfs/;
    }

    location /static/ {
        alias /root/code/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```
:wq!
```
systemctl restart nginx.service
```
```
cd
```
```
cd code
```
```
certbot --nginx -d xkural.hashlabs.in --email tkdhanasekar@gmail.com
```
```
vim /etc/systemd/system/gunicorn.service
```
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/code/
EnvironmentFile=/root/code/.env

ExecStart= /root/code/venv38/bin/gunicorn \
            --access-logfile - \
            --workers 3 \
            --timeout 500 \
            --bind unix:/run/gunicorn.sock \
            tirukkuralweb.wsgi:application
TimeoutStopSec=500
[Install]
WantedBy=multi-user.target
```
:wq!
```
vim /etc/systemd/system/gunicorn.socket
```
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=root
SocketGroup=www-data
SocketMode=0660

[Install]
WantedBy=sockets.target
```
:wq!
```
systemctl daemon-reload
```
```
systemctl enable gunicorn.service
```
```
systemctl enable gunicorn.socket
```
```
systemctl restart gunicorn.service
```
```
systemctl restart nginx.service
```
```
vim /root/code/tirukkuralweb/settings.py
```
```
ALLOWED_HOSTS = [
    "xkural.hashlabs.in",
]

CSRF_TRUSTED_ORIGINS = [
    "https://xkural.hashlabs.in",
]
```
:wq!
```
sudo mkdir -p /var/www/tirukkuralweb/static
```
```
sudo cp -a /root/code/static/. /var/www/tirukkuralweb/static/
```
```
sudo chown -R root:www-data /var/www/tirukkuralweb/static
```
```
sudo chmod -R 755 /var/www/tirukkuralweb/static
```
```
vim /etc/nginx/conf.d/kural.conf
```
```
    location /static/ {
        alias /var/www/tirukkuralweb/static/;
    }
```
:wq!
```
systemctl daemon-reload && systemctl restart gunicorn.service && systemctl restart gunicorn.socket && systemctl restart nginx && systemctl reload nginx && nginx -t
```

https://xkural.hashlabs.in/login/
