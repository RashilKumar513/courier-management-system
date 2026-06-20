from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Courier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    available = db.Column(db.Boolean, default=True)
    shipments = db.relationship('Shipment', backref='courier', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'vehicle_type': self.vehicle_type,
            'available': self.available
        }

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_address = db.Column(db.String(200), nullable=False)
    receiver_name = db.Column(db.String(100), nullable=False)
    receiver_address = db.Column(db.String(200), nullable=False)
    package_description = db.Column(db.String(200), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime, nullable=True)
    courier_id = db.Column(db.Integer, db.ForeignKey('courier.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender_name': self.sender_name,
            'sender_address': self.sender_address,
            'receiver_name': self.receiver_name,
            'receiver_address': self.receiver_address,
            'package_description': self.package_description,
            'weight': self.weight,
            'status': self.status,
            'created_date': self.created_date.strftime("%Y-%m-%d %H:%M:%S"),
            'delivery_date': self.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if self.delivery_date else None,
            'courier_id': self.courier_id
        }