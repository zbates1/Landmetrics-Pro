
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

bash
git clone <repo-url>
cd <repo-directory>
pip install -r requirements.txt


## Running The App

bash
python main.py


### Prerequisites

Before you begin, ensure you have both Docker and Docker Compose installed on your machine. These tools are used to create containers and manage multi-container applications.

## 🖥 Viewing The App

Access the application here: [**Localhost Link**](http://127.0.0.1:5000)

---

# Database Access Guide

In both **local development** and **production**, you may need to access and interact with the databases through the CLI. Below are instructions for local interaction with an SQLite database in development, as well as production-ready SSH commands to access the Heroku Postgres database.

The CLI commands will allow you to test your db_utils functions. 

However, if you need to check your database schema after a migration, you will need to use PgAdmin on your desktop (development/local) and then dataclips on Heroku PostgreSQL (production).

---

## Local Development with website module

To interact with the PostgreSQL in local development, use our custom python package, website.

### **How to Download Website Package**
bash
# Run the following command in the root of your project:
pip install -e .


This command downloads your website folder as a python package, avoiding relative import issues, and allows you to interact with database easily through python CLI.
 

### Add a new user
bash
from website.db_utils import add_user
add_user(email="test@example.com", password="password123", first_name="Test")

### Add a new device for a user Example: Add a device for a user with user_id=1 (use list_users() to find the user_id):
bash
from website.db_utils import add_device
add_device(name="Knee Tracker", device_type="Physical Therapy Device", serial_number="SN123456", user_id=1)

### Add new data for a device Example: Add data for a device using its serial number (SN123456):
bash
from website.db_utils import add_device_data
add_device_data(serial_number="SN123456", value1=50.5, value2=30.7)


## Production-database connection:

This first method allows you to interface in your production environment with Flask Shell

## Accessing Database Utilities in Production with Flask Shell

This first method allows you to interface in your production environment with Flask Shell

In production, use Flask Shell or SQLAlchemy with the connection string from your environment variables (usually DATABASE_URL for Heroku).

### 1. **Connect to the Postgres Database via Heroku**
bash
heroku login


### 2. Set FLASK_APP in Heroku Config Vars **this method works with Landmetrics-Pro**:

If you make any database changes, you may need to go through heroku bash and do a flask db migrate

bash
heroku config:set FLASK_APP=main:app --app landmetrics-pro

### 3. Run the Flask Shell:
bash
heroku run bash --app landmetrics-pro


## Method 2: Access Heroku Postgres DB CLI
You can do this from your local VSCode IDE -> you do need to be in WSL for a windows machine!

### Download postgres on WSL or Apple Machine
bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

### Connect to Postgres DB in your bash terminal:
bash
psql postgres://user:pass@hostname:5432/dbname # your DATABASE_URL

Now you can use the postgres interface to alter your databases. This is for more high-level stuff, like deleting tables, checking migrations, and such, whilst the commands above are for admin-user purposes


# API Connections CLI:
You will need to switch to Git Bash to use this command on Windows, you could switch to WSL, but then the IP address becomes finicky to work with. 

### Local Development CURL:
bash
curl -X POST http://127.0.0.1:5000/api/data -H "Content-Type: application/json" -H "X-API-Key: SECRETKEY" -d @cleaned_data.json

### Now, how to do it in production Heroku Postgres DB
bash
curl -X POST https://landmetrics-pro-94d7ef7fc253.herokuapp.com/api/data \
     -H "Content-Type: application/json" \
     -d @data.json


## 🌟 Future Developments

Explore and implement the following to enhance functionality:

1. 🚀 [**Deployment Strategies**](https://medium.com/@niketl16/best-deployment-strategies-for-application-f4600ed4dd2) - Learn the best practices for deploying applications.
2. 📚 [**12-Factor App Philosophy**](https://12factor.net/) - Understand the principles for building scalable and maintainable software.
3. 🧑‍💻 **Celery for Task Management**:
   - [Understanding Celery Workers](https://ankurdhuriya.medium.com/understanding-celery-workers-concurrency-prefetching-and-heartbeats-85707f28c506)
   - [Celery Part 1](https://medium.com/scalereal/understanding-celery-part-1-why-use-celery-and-what-is-celery-b96bf958cd80) - Is Celery exclusive to Python?
4. 🌐 **Implement Terraform**: Explore infrastructure as code for better resource management.
5. 🌍 **Custom Domain Name**: Acquire and setup a domain for the project.

