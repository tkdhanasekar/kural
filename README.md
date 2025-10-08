# kuralweb

## Basic Packages for server setup (optional for local)
```shell
apt-get install git nginx python3-dev python3-pip python3-virtualenv
```

### Clone the Repo
```shell
git clone https://github.com/fossbalaji/kuralweb.git
```

## change the directory
```shell
cd kuralweb
```

## create virtualenv 
```shell
virtualenv venv
```

## Install packages 
```shell
pip install -r requirements.txt
```

## Supporting Packages needed in linux to generate pdfs using wesayprint
```shell
apt-get install python3-cffi libffi-dev libcairo2 libcairo2-dev libpango-1.0-0 libpangocairo-1.0-0
```
## copy the fonts into /usr/share/fonts/truetype/dejavu folder
```shell
cp NotoSansTamil-VariableFont_wdth,wght.ttf /usr/share/fonts/truetype/dejavu/
cp noto-sans-tamil-fonts.ymp /usr/share/fonts/truetype/dejavu/
```

## Activate envsetup.sh
```shell
source envsetup.sh
```
```
python3 manage.py makemigrations
python3 manage.py migrate
```
## Run the migrations
```shell
python manage.py migrate
```


## Run the local server
```shell
python manage.py runserver
```

## Open Browser and check the server
```
http://localhost:8000/
```

