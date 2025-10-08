
```
# ! usr/bin/sh


# Run below steps as root 

apt install python3-pip python3-virtualenv nginx libpangocairo-1.0-0 certbot python3-certbot-nginx

# create code folder inside root directory
mkdir code

cd /root/code

# Move the back up code inisde this /root/code folder

# Remove virtualenv if already exists
rm -rf venv

# create virtual env
virtualenv venv
source venv/bin/activate
# Install all the requirements
pip install -r requirements.txt

# set the env from .env file 
export DB_HOST=127.0.0.1
export DB_NAME=tirukkural
export DB_USER=root
export DB_PASS=Dashwood@321
export APP_ENV=prod
export TIME_ZONE=Asia/Kolkata
export FROM_EMAIL=tamilttsweb@gmail.com
export EMAIL_PASS=mypassword
export SERVER_URL=http://kural.hashlabs.in/
export DEBUG=False
export HOST=kural.hashlabs.in

# Run the project and check by 
gunicorn --bind 0.0.0.0:8000 tirukkuralweb.wsgi

# if no error comes then all fine, you can verfiy by http://kural.hashlabs.in:8000/

# cntl+c to stop the server

# do django collectstatic by 
python manage.py collectstatic

# change the nginc user to root  in /etc/nginx/nginx.conf
user root

# Copy the necessary fonts from back to specific folder

cp NotoSansTamil-VariableFont_wdth,wght.ttf /usr/local/share/fonts/

cp noto-sans-tamil-fonts.ymp /usr/local/share/fonts/

# copy the nginx conf file

cp kural.conf /etc/nginx/conf.d/kural.conf

# generate ssl for https
certbot --nginx -d kural.hashlabs.in --email tshrinivasan@gmail.com

# open kural.conf , remove duplicate ssl line if exists
# nano /etc/nginx/conf.d/kural.conf

# remove duplicate ssl lines if found (below 5 lines should come only once)
# listen 443 ssl; # managed by Certbot
# ssl_certificate /etc/letsencrypt/live/kural.hashlabs.in/fullchain.pem; # managed by Certbot
# ssl_certificate_key /etc/letsencrypt/live/kural.hashlabs.in/privkey.pem; # managed by Certbot
# include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
# ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


# copy the guncorn.service and gunicorn.socket file backup into specific folders
cp gunicorn.service /etc/systemd/system/gunicorn.service
cp gunicorn.socket /etc/systemd/system/gunicorn.socket


# dameon reload
systemctl daemon-reload

# Enable guncorn and socket
systemctl enable gunicorn.service
systemctl enable gunicorn.socket

# Finally restart all the services
systemctl restart gunicorn.service
systemctl restart nginx.service

# Before closing server , take backup, 
# since DB is sqlite which is stored inside codebase
# make sure to take back up of /root/code and server confs

```



