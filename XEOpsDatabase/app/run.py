# -*- encoding: utf-8 -*-

try:
    from flask_migrate import Migrate
    from sys import exit
    from decouple import config
    import app.base.routes as routes

    from config import config_dict
    from app import create_app, db
except ImportError as error:
    print(error)

# WARNING: Don't run with debug turned on in production!
DEBUG = config('Prod', default=True)

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    
    # Load the configuration using the default values 
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
routes.app_config = app.config
Migrate(app, db)

if __name__ == "__main__":
    
    app.run(host='192.168.86.248')
