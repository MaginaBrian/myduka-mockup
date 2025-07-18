from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from models import db  # Import db from models.py
from blueprints.auth import auth_bp, RegisterUser, LoginUser, LogoutUser, RefreshToken
from blueprints.items import items_bp, ItemEndpoint, ItemEndpointById
from blueprints.supply_requests import supply_requests_bp, SupplyRequestEndpoint, SupplyRequestEndpointById
from blueprints.stores import stores_bp, StoreEndpoint, StoreEndpointById
from blueprints.users import users_bp, UserEndpoint, UserEndpointById
from blueprints.reports import reports_bp, WeeklyReport, MonthlyReport, AnnualReport

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Initialize db with app
migrate = Migrate(app, db)
jwt = JWTManager(app)
api = Api(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(items_bp, url_prefix='/items')
app.register_blueprint(supply_requests_bp, url_prefix='/supply_requests')
app.register_blueprint(stores_bp, url_prefix='/stores')
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(reports_bp, url_prefix='/reports')

# Add Resources
api.add_resource(RegisterUser, '/auth/register')
api.add_resource(LoginUser, '/auth/login')
api.add_resource(LogoutUser, '/auth/logout')
api.add_resource(RefreshToken, '/auth/refresh')
api.add_resource(ItemEndpoint, '/items')
api.add_resource(ItemEndpointById, '/items/<int:id>')
api.add_resource(SupplyRequestEndpoint, '/supply_requests')
api.add_resource(SupplyRequestEndpointById, '/supply_requests/<int:id>')
api.add_resource(StoreEndpoint, '/stores')
api.add_resource(StoreEndpointById, '/stores/<int:id>')
api.add_resource(UserEndpoint, '/users')
api.add_resource(UserEndpointById, '/users/<int:id>')
api.add_resource(WeeklyReport, '/reports/weekly')
api.add_resource(MonthlyReport, '/reports/monthly')
api.add_resource(AnnualReport, '/reports/annual')

@jwt.unauthorized_loader
def unauthorized_response(callback):
    return {"error": "Missing or invalid token"}, 401

@jwt.invalid_token_loader
def invalid_token_response(callback):
    return {"error": "Invalid token"}, 401

@jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
    return {"error": "Token has expired"}, 401

if __name__ == '__main__':
    app.run(debug=True, port=4000)