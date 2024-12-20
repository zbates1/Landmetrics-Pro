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

## 🔥 Urgent To-Do List

- [ ] 🤖 **Prototype Integration**: Arduino/Raspberry Pi → SQL → Web display.
- [ ] 📊 **Finalize Data Analysis View**: Enhance the interface for better user experience.
- [ ] 💾 **Data Export Method**: Implement a secure and efficient data export functionality.
- [ ] 🐳 **Dockerize Repository**: Setup Docker for consistent development environments (see branches: `tutorial_test` and `main`).
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