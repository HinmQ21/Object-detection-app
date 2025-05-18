from flask import Flask

from routes.main_routes import main_bp
from routes.api_routes import api_bp

from tasks.task_manager import start_cleanup_timer

def create_app():
    app = Flask(__name__, template_folder='template')
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    start_cleanup_timer()
    
    app.run(debug=True)
