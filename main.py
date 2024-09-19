import os
from website import create_app

app = create_app()

if __name__ == '__main__':
    # Dynamically fetch the port from the environment variable or use 5000 by default
    port = int(os.getenv('PORT', 5000))

    # Dynamically enable debug mode if FLASK_DEBUG is set to 1, else default to False
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'

    # Bind to all interfaces on the provided port
    app.run(debug=debug_mode, port=port, host="0.0.0.0")