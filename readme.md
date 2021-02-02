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

<br><br>

# FundooNotes Production Documentation
## Django Application deployment on AWS EC2 Instance
> **Creating Server** :
>* Create a EC2 instance on aws.
>* Select ubuntu 18.04 server.
>* Launch the server.
>* Connect to that instance using .pem file
>* Run the following command on terminal
```bash
 ssh -i "secret_key.pem" ubuntu@server_dns
```
            - Now update and upgrade the server - 
>* Use the following commads 
```bash
    sudo apt-get update
    sudo apt-get upgrate
```
> **Servers requeirements**: 
>* We need two softwares to serve django project:
>*    - Nginx : Actual server to host the Appliction. Django uses the python built-in HTTP server for hosting.
>*    -  Wsgi interface : It acts like a link between nginx server and the application using the mechanism called a unique socket. 
>*   - Unique socket is a mechanism to achieve interprocess communication between two applications.
>* - Gunicorn wsgi interface - The Gunicorn "Green Unicorn" is a Python Web Server Gateway Interface HTTP server.

>* Install python and download venv for the virtual environment.
>* Create a virtual environment and activate it.
>* Install all requirements.
>* Install django :
```bash
        pip3 install django
```
>* Clone your project from the git main branch.
>* Install gunicorn : 
```bash
        pip3 install gunicorn
```
>* Install nginx from ubuntu repo : 
```bash
        sudo apt-get install -y nginx
```
>* Change the security group to allow TCP & HTTP traffic.
>* Got to security groups>inbound rule>Add HTTP>Allow from anywhere>save
>* Now check the server. It has started. It shows the welcome message for nginx.


> **Gunicorn connection** : 
>* - Go to project root. There is a wsgi.py file to connect gunicorn to django applications.
>* - We need to tell gunicorn to use this file to serve applications instead of python builtin HTTP.
>* - Command to connect gunicorn :- 
```bash
         gunicorn --bind 0.0.0.0:8000 fundooNote.wsgi:application
```
>* - Add a security rule for port - 8000 and run the server. Now we can see our application using the public ip with port 8000

<br>

> **Supervisor**
>* If we close the terminal the server stops so we have to set a supervisor. It makes sure that the process our application is always running in the background. It will always run gunicorn in the background.
>*  - Installation Command -
```bash
            sudo apt-get install -y supervisor
```
>*  - We have to create a configuration so that the supervisor can read to start or restart the application.
>*  - Path to conf file is - cd /etc/supervisor/conf.d/
>* - -  Create a gunicorn.conf file here with following script
```bash
[program:gunicorn]
directory=/home/ubuntu/FuntooNoteApp
command=/home/ubuntu/env/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/FuntooNoteApp/app.sock FuntooNote.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/gunicorn.err.log
stdout_logfile=/var/log/gunicorn/gunicorn.out.log

```

>* Now we can use this following command to tell the
supervisor to read the gunicorn file.
>* Create a folder at given path in the command:
```bash
        mkdir /var/log/gunicorn 
        supervisorctl reread
```
>* Command to tell supervisor to run the application the background:
```bash
        sudo supervisorctl update
        sudo supervisorctl status
```
>* Restart supervisor : 
```bash
        sudo supervisorctl reload
```

> Nginx Configuration
>* We have to configure nginx to read from the socket file instead of port 8000.
>* All nginx configuration files are in the following director:
>* - sites-available
>* - Sites-enabled
>* Path to these directories : cd /etc/nginx/sites-available
>* Create a django.conf file here.
```bash
   server {
   listen 80;
   server_name public_ip_address

   location / {
       include proxy_params;
       proxy_pass http://unix:/home/ubuntu/FuntooNoteApp/app.sock;

   }
   
}

```

>* Test the configuration by using -t flag :
 ```
        sudo nginx -t
 ```
>* Enable this configuration : 
```
        sudo ln django.conf /etc/nginx/sites-enabled
```
>* - This command creates a hard link between sites-available and sites-enabled.
>* Restart nginx : 
```     
        sudo service nginx restart
```
>* If this error occurs - nginx: [emerg] could not build server_names_hash, you should increase server_names_hash_bucket_size: 64
Then add this to /etc/nginx/nginx.conf - server_names_hash_bucket_size 64;
>* Reload nginx : 
```
        sudo service nginx restart
```
>* Check status of nginx :
 ```
        sudo systemctl status nginx 
 ```

> **Static files serving**
>* Nginx should serve the static files instead of python. 
>* We have to configure the django.conf file for this also. 
```bash
   server {
   listen 80;
   server_name public_ip_address

   location / {
       include proxy_params;
       proxy_pass http://unix:/home/ubuntu/FuntooNoteApp/app.sock;

   }
   location /media/ {
        autoindex on;
        alias /home/ubuntu/FuntooNoteApp/media;
        }
}

```
>* Then reload nginx server and the static files will be served by nginx.

<br>

> Database Connection
>* Choose RDS from amazon services. 
>* Choose the required database and create a database instance after providing the necessary information.
>* Edit the database connection configuration in settings.py file in the project.
>* Provide the AWS database name and password there and also change the host name with host name provided in AWS database instance.
>* Migrate the changes in the server.
>* Restart gunicorn and nginx both and check the server.
>* Create a new server with AWS host and credentials on PgAdmin or install psql client on Project instance and create database

<br>

> Using a .env File to Store Our Environment Variables
>* Create a file called .env in the project root.
>* First we add .env to our .gitignore—this file is going to be used for secrets, and we don’t ever want them ending up on GitHub.
>* Use the django-decouple package for this.
>* Command to install : 
``` 
        pip install django-decouple
```
>* Use config() to access the env variable from the .env file.
>* Reference : https://pypi.org/project/python-decouple

<br>

> Redis Installation
>* Commands to install and configure redis:
```
        sudo apt update
        sudo apt install redis-server
```
>* Open this file
```
        sudo nano /etc/redis/redis.conf
```
>* * Inside the file, find the supervised directive. This directive allows you to declare an init system to manage Redis as a service, providing you with more control over its operation. The supervised directive is set to no by default. Since you are running Ubuntu, which uses the systemd init system, change this to systemd
>* Restart redis:
```
        sudo systemctl restart redis.service
```
>* Testing redis: 
```
        sudo systemctl status redis

```
>* Reference:
>* * https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04

<br>
<br>

# Jenkins Installation and configuration
> Jenkins is an open-source automation server that offers an easy way to set up a continuous integration and continuous delivery (CI/CD) pipeline.
> Continuous integration (CI) is a DevOps practice in which team members regularly commit their code changes to the version control repository, after which automated builds and tests are run. Continuous delivery (CD) is a series of practices where code changes are automatically built, tested and deployed to production.

> Installing Jenkins 
> Jenkins needs java 8 to be installed on the system
>* Installing Java
```
            sudo apt update
            sudo apt install openjdk-8-jdk
```
>*  Add the Jenkins Debian repository.
>* - Import the GPG keys of the Jenkins repository using the following wget command:
```
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
```
>* - Next, add the Jenkins repository to the system with
```
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
```
>* Install Jenkins
>* - Once the Jenkins repository is enabled, update the apt package list and install the latest version of Jenkins by typing:
```
        sudo apt update
        sudo apt install jenkins
```
>* - Jenkins service will automatically start after the installation process is complete. You can verify it by printing the service status:
```
        systemctl status jenkins
```
>* - You should see something similar to this
```
Output:

● jenkins.service - LSB: Start Jenkins at boot time
Loaded: loaded (/etc/init.d/jenkins; generated)
Active: active (exited) since Wed 2018-08-22 13:03:08 PDT; 2min 16s ago
    Docs: man:systemd-sysv-generator(8)
    Tasks: 0 (limit: 2319)
CGroup: /system.slice/jenkins.service
```
>* Adjusting Firewall
>* * If you are installing Jenkins on a remote Ubuntu server that is protected by a firewall you’ll need to open port 8080. Assuming you are using UFW to manage your firewall, you can open the port with the following command:
```
        sudo ufw allow 8080
```
>* - Verify the change with:
```
        sudo ufw status
```
```
Output:

Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
8080                       ALLOW       Anywhere
OpenSSH (v6)               ALLOW       Anywhere (v6)
8080 (v6)                  ALLOW       Anywhere (v6)
```

> To set up your new Jenkins installation, open your browser, type your domain or IP address followed by port 8080, http://your_ip_or_domain:8080
>* During the installation, the Jenkins installer creates an initial 32-character long alphanumeric password. Use the following command to print the password on your terminal:
```
    sudo cat /var/lib/jenkins/secrets/initialAdminPassword

```
```
Output: 

2115173b548f4e99a203ee99a8732a32
```

>* Copy the password from your terminal, paste it into the Administrator password field and click Continue.
>* Then follow the suggetions given by the server
>* Now Copy the .pem file to jenkins server and configure the jenkins
>* Now Build and changes will be reflected on the instance 





















<br>

## **Contribution**
> When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners(**[Birajit Nath](birajit95@gmail.com)**) of this repository before making a change
## **Author**
> #### Birajit Nath
