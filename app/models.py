from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5432/myduka'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class Merchant(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admins = db.relationship('Admin', backref='merchant', lazy=True)
    stores = db.relationship('Store', backref='merchant', lazy=True)
    updates = db.relationship('Update', backref='merchant', lazy=True)

    def set_password(self, password):
        self.password = hash_password(password)

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clerks = db.relationship('Clerk', backref='admin', lazy=True)
    updates = db.relationship('Update', backref='admin', lazy=True)

    def set_password(self, password):
        self.password = hash_password(password)

class Clerk(db.Model):
    __tablename__ = 'clerks'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
    supply_requests = db.relationship('SupplyRequest', backref='store', lazy=True)
    clerks = db.relationship('Clerk', backref='store', lazy=True)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity_received = db.Column(db.Integer, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    quantity_spoilt = db.Column(db.Integer, default=0)
    buying_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.Boolean, default=False)  # False = not paid, True = paid
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    clerk_id = db.Column(db.Integer, db.ForeignKey('clerks.id'), nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    supply_requests = db.relationship('SupplyRequest', backref='item', lazy=True)
    updates = db.relationship('Update', backref='item', lazy=True)

class SupplyRequest(db.Model):
    __tablename__ = 'supply_requests'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    clerk_id = db.Column(db.Integer, db.ForeignKey('clerks.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, declined
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    updates = db.relationship('Update', backref='supply_request', lazy=True)

class Update(db.Model):
    __tablename__ = 'updates'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)  # e.g., 'payment_updated', 'clerk_deactivated'
    description = db.Column(db.Text, nullable=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    clerk_id = db.Column(db.Integer, db.ForeignKey('clerks.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    supply_request_id = db.Column(db.Integer, db.ForeignKey('supply_requests.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()