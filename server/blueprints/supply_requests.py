from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import SupplyRequest, Clerk, Admin, Merchant, Store, Update, db
from datetime import datetime

supply_requests_bp = Blueprint('supply_requests', __name__)

class SupplyRequestEndpoint(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        if role == 'clerks':
            clerk = Clerk.query.get(user_id)
            if not clerk or not clerk.is_active:
                return {"error": "Account deactivated or not found"}, 403
            requests = SupplyRequest.query.filter_by(clerk_id=user_id).all()
        elif role == 'admins':
            admin = Admin.query.get(user_id)
            if not admin or not admin.is_active:
                return {"error": "Account deactivated or not found"}, 403
            clerks = Clerk.query.filter_by(admin_id=user_id).all()
            requests = SupplyRequest.query.filter(SupplyRequest.clerk_id.in_([c.id for c in clerks])).all()
        elif role == 'merchants':
            merchant = Merchant.query.get(user_id)
            if not merchant or not merchant.is_active:
                return {"error": "Account deactivated or not found"}, 403
            stores = Store.query.filter_by(merchant_id=user_id).all()
            requests = SupplyRequest.query.filter(SupplyRequest.store_id.in_([s.id for s in stores])).all()
        else:
            return {"error": "Unauthorized"}, 403

        return [{
            "id": r.id,
            "item_id": r.item_id,
            "store_id": r.store_id,
            "quantity": r.quantity,
            "status": r.status,
            "requested_at": r.requested_at.isoformat()
        } for r in requests], 200

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'clerks':
            return {"error": "Only clerks can request supplies"}, 403

        data = request.get_json()
        clerk = Clerk.query.get(current_user['id'])
        if not clerk or not clerk.is_active:
            return {"error": "Account deactivated or not found"}, 403

        try:
            supply_request = SupplyRequest(
                item_id=data['item_id'],
                store_id=clerk.store_id,
                clerk_id=clerk.id,
                quantity=data['quantity'],
                status="pending"
            )
            db.session.add(supply_request)
            db.session.add(Update(
                action="supply_request_created",
                description=f"Supply request for item {data['item_id']} created",
                clerk_id=clerk.id,
                supply_request_id=supply_request.id
            ))
            db.session.commit()
            return {"message": "Supply request created successfully", "id": supply_request.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class SupplyRequestEndpointById(Resource):
    @jwt_required()
    def get(self, id):
        supply_request = SupplyRequest.query.get(id)
        if not supply_request:
            return {"error": "Supply request not found"}, 404

        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        if role == 'clerks' and supply_request.clerk_id != user_id:
            return {"error": "Unauthorized"}, 403
        elif role == 'admins':
            clerk = Clerk.query.get(supply_request.clerk_id)
            if not clerk or clerk.admin_id != user_id:
                return {"error": "Unauthorized"}, 403
        elif role == 'merchants':
            store = Store.query.get(supply_request.store_id)
            if not store or store.merchant_id != user_id:
                return {"error": "Unauthorized"}, 403

        return {
            "id": supply_request.id,
            "item_id": supply_request.item_id,
            "store_id": supply_request.store_id,
            "quantity": supply_request.quantity,
            "status": supply_request.status,
            "requested_at": supply_request.requested_at.isoformat()
        }, 200

    @jwt_required()
    def put(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admins':
            return {"error": "Only admins can update supply requests"}, 403

        supply_request = SupplyRequest.query.get(id)
        if not supply_request:
            return {"error": "Supply request not found"}, 404

        admin = Admin.query.get(current_user['id'])
        if not admin or not admin.is_active:
            return {"error": "Account deactivated or not found"}, 403

        clerk = Clerk.query.get(supply_request.clerk_id)
        if not clerk or clerk.admin_id != admin.id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        try:
            supply_request.status = data.get('status', supply_request.status)
            db.session.add(Update(
                action="supply_request_updated",
                description=f"Supply request {id} status set to {supply_request.status}",
                admin_id=admin.id,
                supply_request_id=id
            ))
            db.session.commit()
            return {"message": "Supply request updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500