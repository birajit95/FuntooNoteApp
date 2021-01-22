# **FundooNotes (similar as Google Keep Backend)**
<br>

## **Description**
>### This project's backend is developed as similar of **[Google Keep](https://keep.google.com/)** aplication's backend

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
    pip install -r requirements.txt
```
### **Other Dependencies**
* **PostgresSQL**
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

 * **Redis**
>* Redis is an in memory database which is used as cache memory in this project for fast accessing data
>* Redis download link https://redis.io/download
>* Configuring redis :-
> Create a file name as cache.py and use the following singleton class configuration
```python
import redis
class Cache: 
    obj = None
    @staticmethod
    def getCacheInstance():
        if Cache.obj is None:
            Cache.obj = redis.Redis(host='hostname', port=6379)
        return Cache.obj

```
>* now call the getCachefunction any where and use the cache object
* Celery
>* Celery is used to perform Asynchronised task in django. There might be some cases where synchronised tasks are not feasible like checking reminders, sending emails which is an heavey task, so in such situation we have used celery in this project.
>* Configuration of Celery :-
>* In settings.py add
```python
        CELERY_BROKER_URL = 'broker_url'
        CELERY_RESULT_BACKEND = 'django-db'
        CELERY_CACHE_BACKEND = 'django-cache'
```
>* In project directory create a new file named celery.py and add the following code :-
```python
      import os
      from celery import Celery

      os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

      app = Celery('project_name')
      app.config_from_object('django.conf:settings', namespace='CELERY')
      app.autodiscover_tasks()
      app.conf.beat_schedule = {
          'triggering' : {
              'task': 'Notes.tasks.task_name',
              'schedule': 'time_duration',
              'args': 'optional'
          }
      }
```
>* Add the following code in __init__.py of project directory :-
```python
        from .celery import app as celery_app
        __all__ = ['celery_app']
```
>* Create a file named tasks.py inside an app directory and put all our Celery tasks into this file. Following is a demo structure..
```python
        from celery import shared_task

        @shared_task
        def function_name(optional_param):
          # do some asynchronous task
```
>* Now start 2 servers.
>* 1st one is for worker and 2nd one is for beat
>* This 2 commands should be executed in 2 different terminals separately
```python
        celery -A project_name worker -l info
        celery -A project_name beat -l info
```
* RabbitMQ
>* RabbitMQ is a massage broker which is used here to keep the celery tasks in its Queue
>* Here we need to install erlang before rabbitMQ and then install rabbitMQ
>* erlang Download link : https://erlang.org/download/otp_versions_tree.html
>* RabbitMQ download link : https://www.rabbitmq.com/install-windows.html
>* Now enable the rabbitMQ management using the following command in terminal
```bash
    rabbitmq-plugins enable rabbitmq_management
```
>* Now access the server on  http://localhost:15672
>* use basic credential, username: guest and pass: guest

* SonarQube
>* SonarQube is an analytical tool which analyses the whole project and comes up the analysis results like is there any **errors**, **bugs**, **security hotspots** or **duplicay** found in code.
>* SonarQube download link :  https://www.sonarqube.org/downloads/
>* Now unzip the file and configure the following file inside conf directory
>* In sonar.properties file(example for postgresSQL) :-
```properties
    sonar.jdbc.username=db_user_name
    sonar.jdbc.password=db_password
    sonar.embeddedDatabase.port=9092
    sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube?currentSchema=my_schema
    sonar.web.host=127.0.0.1
    sonar.web.context=
    sonar.web.port=9000(default)
```
>* In wrapper.conf file :-
```conf
    wrapper.java.command=/path/to/my/jdk/bin/java
```

>* Execute the following script to start the server
```
On Linux: bin/linux-x86-64/sonar.sh start
On macOS: bin/macosx-universal-64/sonar.sh start
On Windows: bin/windows-x86-64/StartSonar.bat We can now browse SonarQube at http://localhost:9000 (the default System administrator credentials are admin/admin).
```

>* After server is up and running, we'll need to install one or more SonarScanners on the machine where analysis will be performed.
Use this link to download: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
To run SonarScanner from the zip file, follow these steps:

>* Expand the downloaded file into the directory of your choice. We'll refer to it as $install_directory in the next steps.

>* Update the global settings to point to your SonarQube server by editing $install_directory/conf/sonar-scanner.properties:
```properties
     sonar.host.url=http://localhost:9000
```
>* Add the $install_directory/bin directory to your path.

>* Verify installation by opening a new shell and executing the command sonar-scanner -h (sonar-scanner.bat -h on Windows). Output soulbe be like this:
```
      usage: sonar-scanner [options]
      Options:
      -D,--define <arg>     Define property
      -h,--help             Display help information
      -v,--version          Display version information
      -X,--debug            Produce execution debug output
```
>* Create a configuration file in your project's root directory called sonar-project.properties:
```properties
      sonar.projectKey=my:project
      sonar.projectName=My project
      sonar.projectVersion=1.0
      sonar.sources=.
      sonar.sourceEncoding=UTF-8
```

>* **Launching the project**:
>* Give a project on the server
>* Generate a token
>* Run the following command from the project base directory to launch analysis and pass your authentication token:
```bash
    sonar-scanner -Dsonar.login=myAuthenticationToken
```
>* Now access the server at http://localhost:9000
## **Contribution**
> When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners(**[Birajit Nath](birajit95@gmail.com)**) of this repository before making a change
## **Author**
> #### Birajit Nath
