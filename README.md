# Welcome to Landmetrics Pro GitHub Repository!

![GitHub Repo stars](https://img.shields.io/github/stars/zbates1/Landmetrics-Pro?style=social) ![GitHub last commit](https://img.shields.io/github/last-commit/zbates1/Landmetrics-Pro)

## Overview
**Landmetrics Pro** facilitates physical rehabilitation through advanced data analytics. Our device uploads data to a remote server, allowing users to analyze their physical rehabilitation progress.

![Image Alt text](images\landmetrics_concept.png)


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