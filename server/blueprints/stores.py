from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Store, Merchant, Update, db

stores_bp = Blueprint('stores', __name__)

class StoreEndpoint(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'merchants':
            return {"error": "Only merchants can view stores"}, 403

        merchant = Merchant.query.get(current_user['id'])
        if not merchant.is_active:
            return {"error": "Account deactivated"}, 403

        stores = Store.query.filter_by(merchant_id=merchant.id).all()
        return [{"id": s.id, "name": s.name, "created_at": s.created_at.isoformat()} for s in stores], 200

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'merchants':
            return {"error": "Only merchants can add stores"}, 403

        data = request.get_json()
        merchant = Merchant.query.get(current_user['id'])
        if not merchant.is_active:
            return {"error": "Account deactivated"}, 403

        try:
            store = Store(name=data['name'], merchant_id=merchant.id)
            db.session.add(store)
            db.session.add(Update(
                action="store_added",
                description=f"Store {data['name']} added",
                merchant_id=merchant.id
            ))
            db.session.commit()
            return {"message": "Store added successfully", "id": store.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class StoreEndpointById(Resource):
    @jwt_required()
    def get(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'merchants':
            return {"error": "Only merchants can view store details"}, 403

        store = Store.query.get(id)
        if not store:
            return {"error": "Store not found"}, 404

        if store.merchant_id != current_user['id']:
            return {"error": "Unauthorized"}, 403

        return {
            "id": store.id,
            "name": store.name,
            "created_at": store.created_at.isoformat()
        }, 200

    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'merchants':
            return {"error": "Only merchants can delete stores"}, 403

        store = Store.query.get(id)
        if not store:
            return {"error": "Store not found"}, 404

        if store.merchant_id != current_user['id']:
            return {"error": "Unauthorized"}, 403

        try:
            db.session.delete(store)
            db.session.add(Update(
                action="store_deleted",
                description=f"Store {store.name} deleted",
                merchant_id=current_user['id']
            ))
            db.session.commit()
            return {"message": "Store deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500