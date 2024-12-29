from setuptools import setup, find_packages

setup(
    name='website',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "Flask>=2.2.5",
        "Flask-Admin>=1.6.1",
        "Flask-Login>=0.6.3",
        "Flask-Mail>=0.10.0",
        "Flask-Migrate>=4.0.7",
        "Flask-SQLAlchemy>=3.1.1",
        "Flask-WTF>=1.2.1",
        "numpy>=2.2.1",
        "pandas>=2.2.3",
        "python-dotenv>=1.0.1",
        "SQLAlchemy>=2.0.30",
        "Werkzeug>=2.3.8",
        "psycopg2",
    ],
    extras_require={
        "dev": [
            "alembic>=1.13.3",
            "Mako>=1.3.5",
        ]
    },
    description='This is a sample package for Landmetrics Pro. It helps avoid the common error of relative imports when utilizing python to interface with our database.',
    author='Zane Bates',
    author_email='landmetrics.pro@gmail.com',)
