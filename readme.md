# **FundooNotes (Google Keep Backend clone)**
<br>

## **Description**
>### This project is is developed as an clone of **[Google Keep](https://keep.google.com/)** aplication's backend

>### There are 2 applications in this project
>1. User Application
>2. Note Application

### **User Application**
>### This application contains User creation, authentication realeted all APIs
>### The APIs are listed bellow,
>* User Registration API
>* User Email Verifiaction API
>* User Login API
>* User Logout API
>* Forgot Password API
>* Reset Password API
>* Change Password API
>* Update Profile API
>* Get Profile API
>* Update Profile picture API
#
>### **Note Application**
>### This application contains notes creation, manipulation related APIs
>* Create Note API
>* Update Note API
>* Delete Note API
>* Trash and Untrash Note API
>* Add Label API
>* Delete Label API
>* Get Labels API
>* Label oriented Note creation API
>* Get Notes for specific Label API
>* Search Notes API
>* Collborator removes self email id API
>* Add Reminder API
>* Remove Reminder API

#
## **Prerequisites**
**Language and version** 
>* Python 3
### Modules that are needed to be installed
>* amqp==5.0.2
>* asgiref==3.3.1
>* atomicwrites==1.4.0
>* attrs==20.3.0
>* billiard==3.6.3.0
>* celery==5.0.5
>* certifi==2020.12.5
>* chardet==4.0.0
>* click==7.1.2
>* click-didyoumean==0.0.3
>* click-plugins==1.1.1
>* click-repl==0.1.6
>* colorama==0.4.4
>* coreapi==2.3.3
>* coreschema==0.0.4
>* Django==3.0.5
>* django-celery-beat==2.1.0
>* django-celery-results==2.0.0
>* django-colorful==1.3
>* django-rest-swagger==2.1.2
>* django-timezone-field==4.1.1
>* djangorestframework==3.12.2
>* drf-yasg==1.20.0
>* idna==2.10
>* inflection==0.5.1
>* iniconfig==1.1.1
>* iteration-utilities==0.11.0
>* itypes==1.2.0
>* Jinja2==2.11.2
>* kombu==5.0.2
>* MarkupSafe==1.1.1
>* openapi-codec==1.3.2
>* packaging==20.8
>* Pillow==8.0.1
>* pluggy==0.13.1
>* prompt-toolkit==3.0.10
>* psycopg2==2.8.6
>* py==1.10.0
>* PyJWT==2.0.0
>* pymongo==3.11.2
>* pyparsing==2.4.7
>* pyshorteners==1.0.1
>* pytest==6.2.1
>* pytest-django==4.1.0
>* python-crontab==2.5.1
>* python-dateutil==2.8.1
>* pytz==2020.4
>* redis==3.5.3
>* requests==2.25.1
>* ruamel.yaml==0.16.12
>* ruamel.yaml.clib==0.2.2
>* simplejson==3.17.2
>* six==1.15.0
>* sqlparse==0.2.4
>* toml==0.10.2
>* uritemplate==3.0.1
>* urllib3==1.26.2
>* vine==5.0.0
>* wcwidth==0.2.5
>* xlwt==1.3.0

### **Installing packages**
```
    pip install requirements.txt
```
### **Other Dependencies**
* PostgresSQL
> * PostgresSQL is the database used in this project
>* Postgres Download link https://www.postgresql.org/download/
>* pgAdmin download link https://www.pgadmin.org/download/
>* Database configuration ->
>* In the settings.py file
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database_name',
        'USER': username,
        'PASSWORD': password,
        'HOST': 'host-name',
        'PORT': '5432'
    }
}
```

* Redis
>* Redis is an in memory database which is used as cache memory in this project for fast accessing data
>* Redis download link https://redis.io/download
* Celery
>* Celery is used to perform Asynchronised task in django. There might be some cases where synchronised tasks are not feasible like checking reminders, sending emails which is an heavey task, so in such situation we have used celery in this project.
* RabbitMQ
>* RabbitMQ is a massage broker which is used here to keep the celery tasks in its Queue
>* RabbitMQ Download link https://www.rabbitmq.com/download.html
* SonarQube
>* SonarQube is an analytical tool which analyses the whole project and comes up the analysis results like is there any **errors**, **bugs**, **security hotspots** or **duplicay** found in code.
>* SonarQube download link https://docs.sonarqube.org/latest/setup/install-server/
## **Contribution**
> When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners(**[Birajit Nath](birajit95@gmail.com)**) of this repository before making a change
## **Author**
> #### Birajit Nath
## **Licence**
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()
