from flask import Flask
import os
from auth_routes import auth_bp
from job_routes import job_bp
from dashboard_routes import dashboard_bp
from admin_routes import admin_bp
from company_routes import company_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'surejob-v3-blueprint')

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(job_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)

if __name__ == '__main__':
    from auth_routes import init_db
    init_db()
    app.run(debug=True)
