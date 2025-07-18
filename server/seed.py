from app import app, db
from models import Merchant, Admin, Clerk, Store, Item, SupplyRequest, Update
from datetime import datetime

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed a Merchant
        merchant = Merchant(email="merchant@example.com")
        merchant.set_password("merchant123")
        db.session.add(merchant)

        # Seed a Store
        store = Store(name="Main Store", merchant=merchant)
        db.session.add(store)

        # Seed an Admin
        admin = Admin(email="admin@example.com", merchant=merchant)
        admin.set_password("admin123")
        db.session.add(admin)

        # Seed a Clerk
        clerk = Clerk(email="clerk@example.com", admin=admin, store=store)
        clerk.set_password("clerk123")
        db.session.add(clerk)

        # Seed an Item
        item = Item(
            name="Product A",
            quantity_received=100,
            quantity_in_stock=80,
            quantity_spoilt=5,
            buying_price=10.0,
            selling_price=15.0,
            payment_status=False,
            store=store,
            clerk=clerk
        )
        db.session.add(item)

        # Seed a Supply Request
        supply_request = SupplyRequest(
            item=item,
            store=store,
            clerk=clerk,
            quantity=50,
            status="pending"
        )
        db.session.add(supply_request)

        # Seed an Update
        update = Update(
            action="item_added",
            description="Added Product A to Main Store",
            merchant=merchant,
            item=item
        )
        db.session.add(update)

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()