from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Admin, Clerk, Merchant, Update, db
from datetime import datetime, timedelta
import jwt
from config import Config

users_bp = Blueprint('users', __name__)

class UserEndpoint(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        if role == 'merchants':
            merchant = Merchant.query.get(user_id)
            if not merchant or not merchant.is_active:
                return {"error": "Account deactivated or not found"}, 403
            users = Admin.query.filter_by(merchant_id=user_id).all()
        elif role == 'admins':
            admin = Admin.query.get(user_id)
            if not admin or not admin.is_active:
                return {"error": "Account deactivated or not found"}, 403
            users = Clerk.query.filter_by(admin_id=user_id).all()
        else:
            return {"error": "Unauthorized"}, 403

        return [{
            "id": u.id,
            "email": u.email,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        } for u in users], 200

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']
        data = request.get_json()

        if role == 'merchants' and data['role'] == 'admin':
            merchant = Merchant.query.get(user_id)
            if not merchant or not merchant.is_active:
                return {"error": "Account deactivated or not found"}, 403
            user = Admin(email=data['email'], merchant_id=user_id)
            token = jwt.encode({
                'merchant_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, Config.JWT_SECRET_KEY)
        elif role == 'admins' and data['role'] == 'clerk':
            admin = Admin.query.get(user_id)
            if not admin or not admin.is_active:
                return {"error": "Account deactivated or not found"}, 403
            user = Clerk(email=data['email'], admin_id=user_id, store_id=data['store_id'])
            token = jwt.encode({
                'admin_id': user_id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, Config.JWT_SECRET_KEY)
        else:
            return {"error": "Unauthorized"}, 403

        try:
            user.set_password(data['password'])
            db.session.add(user)
            db.session.add(Update(
                action="user_added",
                description=f"{data['role']} {data['email']} added",
                merchant_id=user_id if role == 'merchants' else None,
                admin_id=user_id if role == 'admins' else None
            ))
            db.session.commit()
            return {"message": "User added successfully", "token": token}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class UserEndpointById(Resource):
    @jwt_required()
    def get(self, id):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        user = Admin.query.get(id) or Clerk.query.get(id)
        if not user:
            return {"error": "User not found"}, 404

        if role == 'merchants':
            if isinstance(user, Admin) and user.merchant_id != user_id:
                return {"error": "Unauthorized"}, 403
        elif role == 'admins':
            if isinstance(user, Clerk) and user.admin_id != user_id:
                return {"error": "Unauthorized"}, 403
        else:
            return {"error": "Unauthorized"}, 403

        return {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }, 200

    @jwt_required()
    def put(self, id):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        user = Admin.query.get(id) or Clerk.query.get(id)
        if not user:
            return {"error": "User not found"}, 404

        if role == 'merchants':
            if isinstance(user, Admin) and user.merchant_id != user_id:
                return {"error": "Unauthorized"}, 403
        elif role == 'admins':
            if isinstance(user, Clerk) and user.admin_id != user_id:
                return {"error": "Unauthorized"}, 403
        else:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        try:
            user.is_active = data.get('is_active', user.is_active)
            db.session.add(Update(
                action="user_updated",
                description=f"User {user.email} {'deactivated' if not user.is_active else 'activated'}",
                merchant_id=user_id if role == 'merchants' else None,
                admin_id=user_id if role == 'admins' else None
            ))
            db.session.commit()
            return {"message": "User updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        user = Admin.query.get(id) or Clerk.query.get(id)
        if not user:
            return {"error": "User not found"}, 404

        if role == 'merchants':
            if isinstance(user, Admin) and user.merchant_id != user_id:
                return {"error": "Unauthorized"}, 403
        elif role == 'admins':
            if isinstance(user, Clerk) and user.admin_id != user_id:
                return {"error": "Unauthorized"}, 403
        else:
            return {"error": "Unauthorized"}, 403

        try:
            db.session.delete(user)
            db.session.add(Update(
                action="user_deleted",
                description=f"User {user.email} deleted",
                merchant_id=user_id if role == 'merchants' else None,
                admin_id=user_id if role == 'admins' else None
            ))
            db.session.commit()
            return {"message": "User deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500