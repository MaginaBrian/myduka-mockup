from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import Merchant, Admin, Clerk, db, hash_password
from datetime import datetime, timedelta
import jwt
from config import Config

auth_bp = Blueprint('auth', __name__)

class RegisterUser(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')  # 'admin' or 'clerk'

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            merchant_id = payload.get('merchant_id') if role == 'admin' else payload.get('admin_id')
            if payload['exp'] < datetime.utcnow().timestamp():
                return {"error": "Token expired"}, 401

            if role == 'admin':
                merchant = Merchant.query.get(merchant_id)
                if not merchant or not merchant.is_active:
                    return {"error": "Invalid merchant"}, 403
                user = Admin(email=email, merchant_id=merchant_id)
            elif role == 'clerk':
                admin = Admin.query.get(merchant_id)
                if not admin or not admin.is_active:
                    return {"error": "Invalid admin"}, 403
                user = Clerk(email=email, admin_id=merchant_id, store_id=data.get('store_id'))
            else:
                return {"error": "Invalid role"}, 400

            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return {"message": "User registered successfully"}, 201
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class LoginUser(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = Merchant.query.filter_by(email=email).first() or \
               Admin.query.filter_by(email=email).first() or \
               Clerk.query.filter_by(email=email).first()

        if not user or user.password != hash_password(password):
            return {"error": "Invalid credentials"}, 401
        if not user.is_active:
            return {"error": "Account is deactivated"}, 403

        access_token = create_access_token(identity={'id': user.id, 'role': user.__tablename__})
        refresh_token = create_refresh_token(identity={'id': user.id, 'role': user.__tablename__})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "role": user.__tablename__
        }, 200

class LogoutUser(Resource):
    @jwt_required()
    def post(self):
        return {"message": "Logged out successfully"}, 200

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}, 200