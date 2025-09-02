import uuid
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.Text, unique=True, nullable=False)
    role = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.Text, nullable=False)
    
    # Relationships
    listings = db.relationship('Listing', backref='supplier', lazy=True, foreign_keys='Listing.supplier_id')
    payments_as_supplier = db.relationship('Payment', backref='supplier', lazy=True, foreign_keys='Payment.supplier_id')
    payments_as_buyer = db.relationship('Payment', backref='buyer', lazy=True, foreign_keys='Payment.buyer_id')
    waiting_list_items = db.relationship('WaitingList', backref='buyer', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.Text, nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    contact = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    supplier_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    payments = db.relationship('Payment', backref='listing', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False)
    transaction_id = db.Column(db.Text, nullable=False)
    supplier_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.String(36), db.ForeignKey('listings.id'), nullable=False)

class WaitingList(db.Model):
    __tablename__ = 'waiting_list'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    item_requested = db.Column(db.Text, nullable=False)
    contact = db.Column(db.Text, nullable=False)
    is_notified = db.Column(db.Text, default='no')
    buyer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
