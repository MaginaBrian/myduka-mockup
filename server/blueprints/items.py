from flask import Blueprint, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Item, Clerk, Admin, Merchant, Store, Update, db
from datetime import datetime

items_bp = Blueprint('items', __name__)

class ItemEndpoint(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        if role == 'clerks':
            clerk = Clerk.query.get(user_id)
            if not clerk or not clerk.is_active:
                return {"error": "Account deactivated or not found"}, 403
            items = Item.query.filter_by(clerk_id=user_id).all()
        elif role == 'admins':
            admin = Admin.query.get(user_id)
            if not admin or not admin.is_active:
                return {"error": "Account deactivated or not found"}, 403
            clerks = Clerk.query.filter_by(admin_id=user_id).all()
            items = Item.query.filter(Item.clerk_id.in_([c.id for c in clerks])).all()
        elif role == 'merchants':
            merchant = Merchant.query.get(user_id)
            if not merchant or not merchant.is_active:
                return {"error": "Account deactivated or not found"}, 403
            stores = Store.query.filter_by(merchant_id=user_id).all()
            items = Item.query.filter(Item.store_id.in_([s.id for s in stores])).all()
        else:
            return {"error": "Unauthorized"}, 403

        return [{
            "id": i.id,
            "name": i.name,
            "quantity_received": i.quantity_received,
            "quantity_in_stock": i.quantity_in_stock,
            "quantity_spoilt": i.quantity_spoilt,
            "buying_price": i.buying_price,
            "selling_price": i.selling_price,
            "payment_status": i.payment_status,
            "store_id": i.store_id
        } for i in items], 200

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'clerks':
            return {"error": "Only clerks can add items"}, 403

        data = request.get_json()
        clerk = Clerk.query.get(current_user['id'])
        if not clerk or not clerk.is_active:
            return {"error": "Account deactivated or not found"}, 403

        try:
            item = Item(
                name=data['name'],
                quantity_received=data['quantity_received'],
                quantity_in_stock=data['quantity_received'],
                quantity_spoilt=data.get('quantity_spoilt', 0),
                buying_price=data['buying_price'],
                selling_price=data['selling_price'],
                payment_status=data.get('payment_status', False),
                store_id=clerk.store_id,
                clerk_id=clerk.id
            )
            db.session.add(item)
            db.session.add(Update(
                action="item_added",
                description=f"Added {data['name']} to store {clerk.store_id}",
                clerk_id=clerk.id,
                item_id=item.id
            ))
            db.session.commit()
            return {"message": "Item added successfully", "id": item.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class ItemEndpointById(Resource):
    @jwt_required()
    def get(self, id):
        item = Item.query.get(id)
        if not item:
            return {"error": "Item not found"}, 404

        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        if role == 'clerks' and item.clerk_id != user_id:
            return {"error": "Unauthorized"}, 403
        elif role == 'admins':
            clerk = Clerk.query.get(item.clerk_id)
            if not clerk or clerk.admin_id != user_id:
                return {"error": "Unauthorized"}, 403
        elif role == 'merchants':
            store = Store.query.get(item.store_id)
            if not store or store.merchant_id != user_id:
                return {"error": "Unauthorized"}, 403

        return {
            "id": item.id,
            "name": item.name,
            "quantity_received": item.quantity_received,
            "quantity_in_stock": item.quantity_in_stock,
            "quantity_spoilt": item.quantity_spoilt,
            "buying_price": item.buying_price,
            "selling_price": item.selling_price,
            "payment_status": item.payment_status,
            "store_id": item.store_id
        }, 200

    @jwt_required()
    def put(self, id):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']

        item = Item.query.get(id)
        if not item:
            return {"error": "Item not found"}, 404

        if role == 'clerks' and item.clerk_id != user_id:
            return {"error": "Unauthorized"}, 403
        elif role == 'admins':
            clerk = Clerk.query.get(item.clerk_id)
            if not clerk or clerk.admin_id != user_id:
                return {"error": "Unauthorized"}, 403
        elif role == 'merchants':
            store = Store.query.get(item.store_id)
            if not store or store.merchant_id != user_id:
                return {"error": "Unauthorized"}, 403

        data = request.get_json()
        try:
            item.quantity_in_stock = data.get('quantity_in_stock', item.quantity_in_stock)
            item.quantity_spoilt = data.get('quantity_spoilt', item.quantity_spoilt)
            if role == 'admins' and 'payment_status' in data:
                item.payment_status = data['payment_status']
                db.session.add(Update(
                    action="payment_updated",
                    description=f"Payment status for {item.name} set to {data['payment_status']}",
                    admin_id=user_id,
                    item_id=item.id
                ))
            db.session.commit()
            return {"message": "Item updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] not in ['admins', 'merchants']:
            return {"error": "Unauthorized"}, 403

        item = Item.query.get(id)
        if not item:
            return {"error": "Item not found"}, 404

        try:
            db.session.delete(item)
            db.session.add(Update(
                action="item_deleted",
                description=f"Item {item.name} deleted",
                admin_id=current_user['id'] if current_user['role'] == 'admins' else None,
                merchant_id=current_user['id'] if current_user['role'] == 'merchants' else None
            ))
            db.session.commit()
            return {"message": "Item deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500