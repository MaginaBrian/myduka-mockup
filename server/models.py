from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class Merchant(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    stores = db.relationship('Store', backref='merchant', lazy=True)
    admins = db.relationship('Admin', backref='merchant', lazy=True)
    updates = db.relationship('Update', backref='merchant', lazy=True)

    def set_password(self, password):
        self.password = hash_password(password)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    clerks = db.relationship('Clerk', backref='admin', lazy=True)
    updates = db.relationship('Update', backref='admin', lazy=True)

    def set_password(self, password):
        self.password = hash_password(password)

class Clerk(db.Model):
    __tablename__ = 'clerks'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    items = db.relationship('Item', backref='clerk', lazy=True)
    supply_requests = db.relationship('SupplyRequest', backref='clerk', lazy=True)
    updates = db.relationship('Update', backref='clerk', lazy=True)

    def set_password(self, password):
        self.password = hash_password(password)

class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('Item', backref='store', lazy=True)
    clerks = db.relationship('Clerk', backref='store', lazy=True)
    supply_requests = db.relationship('SupplyRequest', backref='store', lazy=True)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity_received = db.Column(db.Integer, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    quantity_spoilt = db.Column(db.Integer, nullable=False)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    clerk_id = db.Column(db.Integer, db.ForeignKey('clerks.id'), nullable=False)
    supply_requests = db.relationship('SupplyRequest', backref='item', lazy=True)
    updates = db.relationship('Update', backref='item', lazy=True)

class SupplyRequest(db.Model):
    __tablename__ = 'supply_requests'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    clerk_id = db.Column(db.Integer, db.ForeignKey('clerks.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)

class Update(db.Model):
    __tablename__ = 'updates'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    clerk_id = db.Column(db.Integer, db.ForeignKey('clerks.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    supply_request_id = db.Column(db.Integer, db.ForeignKey('supply_requests.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)