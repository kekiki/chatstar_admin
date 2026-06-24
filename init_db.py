from database import engine, Base, SessionLocal
from models import Admin, App, User, Streamer, Order, Payment, Activity
from datetime import datetime, timedelta, date
import random

def init_database():
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Activity).delete()
        db.query(Payment).delete()
        db.query(Order).delete()
        db.query(Streamer).delete()
        db.query(User).delete()
        db.query(App).delete()
        db.query(Admin).delete()
        db.commit()
        
        # Create admin user
        print("Creating admin user...")
        admin = Admin(
            username='admin',
            email='admin@chatstar.com',
            is_active=True
        )
        admin.set_password('admin123')
        db.add(admin)
        db.commit()
        
        # Create sample apps
        print("Creating sample apps...")
        apps = []
        app_names = ['ChatStar Live', 'ChatStar Dating', 'ChatStar Gaming']
        
        for name in app_names:
            import secrets
            app = App(
                name=name,
                app_key=secrets.token_urlsafe(32),
                description=f'{name} - A popular social platform',
                icon_url=f'https://via.placeholder.com/64/0ea5e9/ffffff?text={name[0]}',
                is_active=True,
                config={'max_users': 10000, 'features': ['chat', 'video', 'voice']}
            )
            db.add(app)
            apps.append(app)
        
        db.commit()
        
        # Create sample users
        print("Creating sample users...")
        for app in apps:
            for i in range(50):
                user = User(
                    app_id=app.id,
                    username=f'user_{app.id}_{i}',
                    email=f'user_{app.id}_{i}@example.com',
                    phone=f'138{random.randint(10000000, 99999999)}',
                    is_active=True,
                    is_premium=random.choice([True, False]),
                    total_spent=random.uniform(0, 500),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    last_active=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                )
                db.add(user)
        
        db.commit()
        
        # Create sample streamers
        print("Creating sample streamers...")
        for app in apps:
            for i in range(20):
                streamer = Streamer(
                    app_id=app.id,
                    username=f'streamer_{app.id}_{i}',
                    display_name=f'主播 {i+1}',
                    avatar_url=f'https://via.placeholder.com/64/10b981/ffffff?text={i+1}',
                    bio=f'这是主播 {i+1} 的个人简介',
                    is_active=True,
                    is_verified=random.choice([True, False]),
                    follower_count=random.randint(100, 10000),
                    total_earnings=random.uniform(0, 10000),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    last_stream=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
                )
                db.add(streamer)
        
        db.commit()
        
        # Create sample orders
        print("Creating sample orders...")
        users = db.query(User).all()
        for user in users:
            num_orders = random.randint(0, 10)
            for i in range(num_orders):
                order = Order(
                    app_id=user.app_id,
                    user_id=user.id,
                    order_no=f'ORD{datetime.utcnow().strftime("%Y%m%d%H%M%S")}{random.randint(1000, 9999)}',
                    amount=random.uniform(9.99, 199.99),
                    status=random.choice(['completed', 'pending', 'cancelled', 'refunded']),
                    payment_method=random.choice(['wechat', 'alipay', 'credit_card']),
                    product_type=random.choice(['subscription', 'virtual_item', 'gift']),
                    product_id=f'prod_{random.randint(1, 100)}',
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                if order.status == 'completed':
                    order.completed_at = order.created_at + timedelta(minutes=random.randint(1, 60))
                db.add(order)
        
        db.commit()
        
        # Create sample payments
        print("Creating sample payments...")
        orders = db.query(Order).filter(Order.status == 'completed').all()
        for order in orders:
            payment = Payment(
                app_id=order.app_id,
                user_id=order.user_id,
                order_id=order.id,
                amount=order.amount,
                payment_type=random.choice(['new', 'renewal']),
                created_at=order.completed_at
            )
            db.add(payment)
        
        db.commit()
        
        # Create sample activities
        print("Creating sample activities...")
        for user in users:
            for i in range(30):
                activity_date = date.today() - timedelta(days=i)
                activity = Activity(
                    app_id=user.app_id,
                    user_id=user.id,
                    activity_date=activity_date,
                    session_count=random.randint(0, 5),
                    duration_seconds=random.randint(0, 7200)
                )
                db.add(activity)
        
        db.commit()
        
        print("\n" + "="*50)
        print("Database initialization completed successfully!")
        print("="*50)
        print(f"\nAdmin login:")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"\nCreated:")
        print(f"  {len(apps)} apps")
        print(f"  {db.query(User).count()} users")
        print(f"  {db.query(Streamer).count()} streamers")
        print(f"  {db.query(Order).count()} orders")
        print(f"  {db.query(Payment).count()} payments")
        print(f"  {db.query(Activity).count()} activities")
        
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    init_database()
