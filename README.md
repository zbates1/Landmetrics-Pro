# Welcome to Landmetrics Pro GitHub Repository!

![GitHub Repo stars](https://img.shields.io/github/stars/zbates1/Landmetrics-Pro?style=social) ![GitHub last commit](https://img.shields.io/github/last-commit/zbates1/Landmetrics-Pro)

## Overview
**Landmetrics Pro** facilitates physical rehabilitation through advanced data analytics. Our device uploads data to a remote server, allowing users to analyze their physical rehabilitation progress.

![Image Alt text](./website/static/images/example_usage_stock_3.png)


- **Sign In**: After signing in, access and export your curated data directly from our web platform.

This repository's structure is inspired by the following resources:
- [YouTube Tutorial](https://www.youtube.com/watch?v=dam0GPOAvVI&list=LL&index=27)
- [TechWithTim's Flask Web App Tutorial on GitHub](https://github.com/techwithtim/Flask-Web-App-Tutorial)

## Setup & Installation

Ensure you have the latest version of Python installed. Then, clone and set up the project environment:

```bash
git clone <repo-url>
cd <repo-directory>
pip install -r requirements.txt
```

## Running The App

```bash
python main.py
```

## Running the Application with Docker and Docker Compose

This project supports both Docker and Docker Compose for easy setup and deployment. Below are the instructions on how to utilize these tools in development and production environments.

### Prerequisites

Before you begin, ensure you have both Docker and Docker Compose installed on your machine. These tools are used to create containers and manage multi-container applications.

### Docker

You can build and run the application using Docker. Here are the basic commands:

1. **Building the Docker Image**

   Build the Docker image using the following command:

```bash
   docker build -t my-flask-app .
```

   This command builds a Docker image named my-flask-app based on the instructions in your Dockerfile.

2. **Running the Container**

   Run your application by starting a container from the image:

```bash
   docker run -p 5000:5000 --name my-running-app my-flask-app
```

   This command runs the container and maps port 5000 of the container to port 5000 on your host, allowing you to access the application via http://localhost:5000.

### Docker Compose

Docker Compose allows you to manage the application with its services defined in the docker-compose.yml file.

**Development Environment**
To start the development environment, use the following command:

```bash
docker-compose up app
```

This will start the application in development mode, with live reloads and debugging enabled.

**Production Environment**

To deploy the application in a production environment, use:

```bash
docker-compose up app-prod
```

This will start the application using Gunicorn, optimized for production. Note that this setup is still in the production testing phase and may require further adjustments before a full production deployment.

**Stopping and Removing Containers**

To stop the running containers and remove them, you can use the following Docker Compose command:

```bash
docker-compose down
```

This command stops all the running services defined in your docker-compose.yml file and removes the containers, networks, and volumes created by them.


## 🖥 Viewing The App

Access the application here: [**Localhost Link**](http://127.0.0.1:5000)

---

# Database Access Guide

In both **local development** and **production**, you may need to access and interact with the databases through the CLI. Below are instructions for local interaction with an SQLite database in development, as well as production-ready SSH commands to access the Heroku Postgres database.

---

## Local Development with Flask Shell

To interact with the SQLite database during local development, use the Flask shell.

### **How to Access Flask Shell**
```bash
# Run the following command in the root of your project:
flask --app website shell
```

This command opens the Flask shell, allowing you to manually add or interact with the database using utility functions.

## Local Development/Database Access with Flask Shell and Example Commands 
Check website/db_utils.py for a comprehensive list of the functions and commands.

### Add a new user
```bash
from website.db_utils import add_user
add_user(email="test@example.com", password="password123", first_name="Test")
```
### Add a new device for a user Example: Add a device for a user with user_id=1 (use list_users() to find the user_id):
```bash
from website.db_utils import add_device
add_device(name="Knee Tracker", device_type="Physical Therapy Device", serial_number="SN123456", user_id=1)
```
### Add new data for a device Example: Add data for a device using its serial number (SN123456):
```bash
from website.db_utils import add_device_data
add_device_data(serial_number="SN123456", value1=50.5, value2=30.7)
```

## Local Development Example CLI Commands 
For easier interaction without entering the Flask shell, you can use CLI commands. Here are a few examples:

### List all users:
```bash
python db_utils.py --list-users
```
### List devices for a user with user_id=1:
```bash
python db_utils.py --list-devices-for-user 1
```

You can definitely use sqlite3 db_name to access your db and use SQL queries as an alternative!

## Two ways to Access production-database:

## Method 1: Accessing Database Utilities in Production with Flask Shell

This first method allows you to interface in your production environment with Flask Shell

In production, use Flask Shell or SQLAlchemy with the connection string from your environment variables (usually DATABASE_URL for Heroku).

### 1. **Connect to the Postgres Database via Heroku**
```bash
heroku login
```

### 2. Set FLASK_APP in Heroku Config Vars **this method works with Landmetrics-Pro**:

If you make any database changes, you may need to go through heroku bash and do a flask db migrate

```bash
heroku config:set FLASK_APP=main:app --app landmetrics-pro
```
### 3. Run the Flask Shell:
```bash
heroku run --app landmetrics-pro flask shell
```
or
```bash
heroku run --app landmetrics-pro flask --app main:app shell
```

## Method 2: Access Heroku Postgres DB CLI
You can do this from your local VSCode IDE -> you do need to be in WSL for a windows machine!

### Download postgres on WSL or Apple Machine
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```
### 2. Connect to Postgres DB in your bash terminal:
```bash
psql postgres://user:pass@hostname:5432/dbname # your DATABASE_URL
```
Now you can use the postgres interface to alter your databases. This is for more high-level stuff, like deleting tables, checking migrations, and such, whilst the commands above are for admin-user purposes

## Connecting to Heroku Bash
You may need to do this to manually delete some scripts on the production server, such as migration scripts in my case. 

### Login to Heroku: If you haven't logged in yet, run
```bash
heroku login
```
### Connect to Postgres DB in your bash terminal:
```bash
heroku run bash --app your-app-name # landmetrics-pro for us
```

# API Connections CLI:

## Development/Local SQLITE3 DB
1. switch to WSL
2. find IP of flask
3. use CURL
### send CURL command:
```bash
curl -X POST http://172.23.112.1:5000/api/data -H "Content-Type: application/json" -d @data.json
```
## Now, how to do it in production Heroku Postgres DB
```bash
curl -X POST https://landmetrics-pro-94d7ef7fc253.herokuapp.com/api/data \
     -H "Content-Type: application/json" \
     -d @data.json
```


## 🔥 Urgent To-Do List

- [ ] 🤖 **Prototype Integration**: Arduino/Raspberry Pi → SQL → Web display.
- [ ] 📊 **Finalize Data Analysis View**: Enhance the interface for better user experience.
- [ ] 🔒 **Environment Variables**: Establish secure deployment practices. (see 'user_data.py' line 14 to see how best practices for getting env varaibles in your py scripts)

---

## 🌟 Future Developments

Explore and implement the following to enhance functionality:

1. 🚀 [**Deployment Strategies**](https://medium.com/@niketl16/best-deployment-strategies-for-application-f4600ed4dd2) - Learn the best practices for deploying applications.
2. 📚 [**12-Factor App Philosophy**](https://12factor.net/) - Understand the principles for building scalable and maintainable software.
3. 🧑‍💻 **Celery for Task Management**:
   - [Understanding Celery Workers](https://ankurdhuriya.medium.com/understanding-celery-workers-concurrency-prefetching-and-heartbeats-85707f28c506)
   - [Celery Part 1](https://medium.com/scalereal/understanding-celery-part-1-why-use-celery-and-what-is-celery-b96bf958cd80) - Is Celery exclusive to Python?
4. 🌐 **Implement Terraform**: Explore infrastructure as code for better resource management.
5. 🌍 **Custom Domain Name**: Acquire and setup a domain for the project.