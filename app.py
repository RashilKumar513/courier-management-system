from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import db, Courier, Shipment
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courier_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Status options for shipments
STATUS_OPTIONS = ['Pending', 'In Transit', 'Out for Delivery', 'Delivered', 'Cancelled']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/couriers')
def couriers():
    all_couriers = Courier.query.all()
    return render_template('couriers.html', couriers=all_couriers)

@app.route('/add_courier', methods=['GET', 'POST'])
def add_courier():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        vehicle_type = request.form['vehicle_type']
        
        new_courier = Courier(name=name, phone=phone, vehicle_type=vehicle_type)
        db.session.add(new_courier)
        db.session.commit()
        
        flash('Courier added successfully!', 'success')
        return redirect(url_for('couriers'))
    
    return render_template('add_courier.html')

@app.route('/delete_courier/<int:id>')
def delete_courier(id):
    courier = Courier.query.get_or_404(id)
    
    # Check if courier has active shipments
    active_shipments = Shipment.query.filter_by(courier_id=id).filter(
        Shipment.status.in_(['Pending', 'In Transit', 'Out for Delivery'])
    ).all()
    
    if active_shipments:
        flash('Cannot delete courier with active shipments!', 'danger')
        return redirect(url_for('couriers'))
    
    db.session.delete(courier)
    db.session.commit()
    flash('Courier deleted successfully!', 'success')
    return redirect(url_for('couriers'))

@app.route('/shipments')
def shipments():
    all_shipments = Shipment.query.all()
    return render_template('shipments.html', shipments=all_shipments, status_options=STATUS_OPTIONS)

@app.route('/add_shipment', methods=['GET', 'POST'])
def add_shipment():
    available_couriers = Courier.query.filter_by(available=True).all()
    
    if request.method == 'POST':
        sender_name = request.form['sender_name']
        sender_address = request.form['sender_address']
        receiver_name = request.form['receiver_name']
        receiver_address = request.form['receiver_address']
        package_description = request.form['package_description']
        weight = float(request.form['weight'])
        courier_id = int(request.form['courier_id'])
        
        # Mark courier as unavailable
        courier = Courier.query.get(courier_id)
        courier.available = False
        
        new_shipment = Shipment(
            sender_name=sender_name,
            sender_address=sender_address,
            receiver_name=receiver_name,
            receiver_address=receiver_address,
            package_description=package_description,
            weight=weight,
            courier_id=courier_id
        )
        
        db.session.add(new_shipment)
        db.session.commit()
        
        flash('Shipment created successfully!', 'success')
        return redirect(url_for('shipments'))
    
    return render_template('add_shipment.html', couriers=available_couriers)

@app.route('/update_status/<int:id>', methods=['GET', 'POST'])
def update_status(id):
    shipment = Shipment.query.get_or_404(id)
    
    if request.method == 'POST':
        new_status = request.form['status']
        shipment.status = new_status
        
        # If delivered, update delivery date and free the courier
        if new_status == 'Delivered':
            shipment.delivery_date = datetime.utcnow()
            courier = Courier.query.get(shipment.courier_id)
            courier.available = True
        
        db.session.commit()
        flash('Status updated successfully!', 'success')
        return redirect(url_for('shipments'))
    
    return render_template('update_status.html', shipment=shipment, status_options=STATUS_OPTIONS)

@app.route('/delete_shipment/<int:id>')
def delete_shipment(id):
    shipment = Shipment.query.get_or_404(id)
    
    # Free the courier if shipment was active
    if shipment.status != 'Delivered' and shipment.status != 'Cancelled':
        courier = Courier.query.get(shipment.courier_id)
        courier.available = True
    
    db.session.delete(shipment)
    db.session.commit()
    flash('Shipment deleted successfully!', 'success')
    return redirect(url_for('shipments'))

@app.route('/report')
def report():
    total_couriers = Courier.query.count()
    total_shipments = Shipment.query.count()
    
    # Status counts
    status_counts = {}
    for status in STATUS_OPTIONS:
        count = Shipment.query.filter_by(status=status).count()
        status_counts[status] = count
    
    # Available couriers
    available_couriers = Courier.query.filter_by(available=True).count()
    
    return render_template('report.html', 
                          total_couriers=total_couriers,
                          total_shipments=total_shipments,
                          status_counts=status_counts,
                          available_couriers=available_couriers)

@app.route('/search_shipments')
def search_shipments():
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return redirect(url_for('shipments'))
    
    results = Shipment.query.filter(
        (Shipment.sender_name.ilike(f'%{query}%')) | 
        (Shipment.receiver_name.ilike(f'%{query}%')) |
        (Shipment.id == query if query.isdigit() else False)
    ).all()
    
    return render_template('shipments.html', shipments=results, status_options=STATUS_OPTIONS, search_query=query)

if __name__ == '__main__':
    app.run(debug=True)