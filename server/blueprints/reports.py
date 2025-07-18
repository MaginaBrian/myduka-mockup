from flask import Blueprint, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Item, Store, Merchant, Admin, Clerk, db
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

class WeeklyReport(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']
        start_date = datetime.utcnow() - timedelta(days=7)

        if role == 'merchants':
            merchant = Merchant.query.get(user_id)
            if not merchant.is_active:
                return {"error": "Account deactivated"}, 403
            stores = Store.query.filter_by(merchant_id=user_id).all()
            items = Item.query.filter(
                Item.store_id.in_([s.id for s in stores]),
                Item.received_at >= start_date
            ).all()
        elif role == 'admins':
            admin = Admin.query.get(user_id)
            if not admin.is_active:
                return {"error": "Account deactivated"}, 403
            clerks = Clerk.query.filter_by(admin_id=user_id).all()
            items = Item.query.filter(
                Item.clerk_id.in_([c.id for c in clerks]),
                Item.received_at >= start_date
            ).all()
        elif role == 'clerks':
            clerk = Clerk.query.get(user_id)
            if not clerk.is_active:
                return {"error": "Account deactivated"}, 403
            items = Item.query.filter_by(clerk_id=user_id, received_at=start_date).all()
        else:
            return {"error": "Unauthorized"}, 403

        report = {
            "total_items": len(items),
            "total_stock": sum(i.quantity_in_stock for i in items),
            "total_spoilt": sum(i.quantity_spoilt for i in items),
            "paid_items": len([i for i in items if i.payment_status]),
            "unpaid_items": len([i for i in items if not i.payment_status]),
            "items": [{"name": i.name, "quantity_in_stock": i.quantity_in_stock, "quantity_spoilt": i.quantity_spoilt} for i in items]
        }
        return report, 200

class MonthlyReport(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']
        start_date = datetime.utcnow() - timedelta(days=30)

        if role == 'merchants':
            merchant = Merchant.query.get(user_id)
            if not merchant.is_active:
                return {"error": "Account deactivated"}, 403
            stores = Store.query.filter_by(merchant_id=user_id).all()
            items = Item.query.filter(
                Item.store_id.in_([s.id for s in stores]),
                Item.received_at >= start_date
            ).all()
        elif role == 'admins':
            admin = Admin.query.get(user_id)
            if not admin.is_active:
                return {"error": "Account deactivated"}, 403
            clerks = Clerk.query.filter_by(admin_id=user_id).all()
            items = Item.query.filter(
                Item.clerk_id.in_([c.id for c in clerks]),
                Item.received_at >= start_date
            ).all()
        elif role == 'clerks':
            clerk = Clerk.query.get(user_id)
            if not clerk.is_active:
                return {"error": "Account deactivated"}, 403
            items = Item.query.filter_by(clerk_id=user_id, received_at=start_date).all()
        else:
            return {"error": "Unauthorized"}, 403

        report = {
            "total_items": len(items),
            "total_stock": sum(i.quantity_in_stock for i in items),
            "total_spoilt": sum(i.quantity_spoilt for i in items),
            "paid_items": len([i for i in items if i.payment_status]),
            "unpaid_items": len([i for i in items if not i.payment_status]),
            "items": [{"name": i.name, "quantity_in_stock": i.quantity_in_stock, "quantity_spoilt": i.quantity_spoilt} for i in items]
        }
        return report, 200

class AnnualReport(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        role = current_user['role']
        user_id = current_user['id']
        start_date = datetime.utcnow() - timedelta(days=365)

        if role == 'merchants':
            merchant = Merchant.query.get(user_id)
            if not merchant.is_active:
                return {"error": "Account deactivated"}, 403
            stores = Store.query.filter_by(merchant_id=user_id).all()
            items = Item.query.filter(
                Item.store_id.in_([s.id for s in stores]),
                Item.received_at >= start_date
            ).all()
        elif role == 'admins':
            admin = Admin.query.get(user_id)
            if not admin.is_active:
                return {"error": "Account deactivated"}, 403
            clerks = Clerk.query.filter_by(admin_id=user_id).all()
            items = Item.query.filter(
                Item.clerk_id.in_([c.id for c in clerks]),
                Item.received_at >= start_date
            ).all()
        elif role == 'clerks':
            clerk = Clerk.query.get(user_id)
            if not clerk.is_active:
                return {"error": "Account deactivated"}, 403
            items = Item.query.filter_by(clerk_id=user_id, received_at=start_date).all()
        else:
            return {"error": "Unauthorized"}, 403

        report = {
            "total_items": len(items),
            "total_stock": sum(i.quantity_in_stock for i in items),
            "total_spoilt": sum(i.quantity_spoilt for i in items),
            "paid_items": len([i for i in items if i.payment_status]),
            "unpaid_items": len([i for i in items if not i.payment_status]),
            "items": [{"name": i.name, "quantity_in_stock": i.quantity_in_stock, "quantity_spoilt": i.quantity_spoilt} for i in items]
        }
        return report, 200