"""Application entry point."""

import os
from src.presentation.app_factory import create_app

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False), host='127.0.0.1', port=5000)
