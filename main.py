# main.py
import os
from website import create_app
from website.config import DevelopmentConfig, ProductionConfig

env = os.getenv('FLASK_ENV', 'development') # tag: H10 error code -> "App Crashed". You may need to make sure that you set the 'production' environment for Heroku, especially if you see a database error. 

if env == 'production': # tag: set up ENV variables in Heroku GUI or in Procfile
    config_class = ProductionConfig
    print(f'Running Landmetrics-Pro in {env} mode')
else:
    config_class = DevelopmentConfig
    print(f'Running Landmetrics-Pro in {env} mode')

app = create_app(config_class)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(port=port, host='0.0.0.0')
