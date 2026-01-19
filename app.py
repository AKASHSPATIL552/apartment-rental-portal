from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/apartment_rental')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Tower(db.Model):
    __tablename__ = 'towers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    floors = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    units = db.relationship('Unit', backref='tower', lazy=True, cascade='all, delete-orphan')

class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    tower_id = db.Column(db.Integer, db.ForeignKey('towers.id'), nullable=False)
    unit_number = db.Column(db.String(20), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    area_sqft = db.Column(db.Integer)
    rent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    bookings = db.relationship('Booking', backref='unit', lazy=True)

class Amenity(db.Model):
    __tablename__ = 'amenities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    icon = db.Column(db.String(50))

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    move_in_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)

class Lease(db.Model):
    __tablename__ = 'leases'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    rent_amount = db.Column(db.Numeric(10, 2), nullable=False)
    security_deposit = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='active')

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    lease_id = db.Column(db.Integer, db.ForeignKey('leases.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='completed')

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

# Public Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/browse')
def browse():
    return render_template('browse.html')

# Admin Routes
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        return redirect(url_for('index'))
    return render_template('admin.html')

# API Routes - Authentication
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        full_name=data.get('full_name'),
        phone=data.get('phone')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_admin
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    user = User.query.get(session['user_id'])
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'is_admin': user.is_admin
    }), 200

# API Routes - Units
@app.route('/api/units', methods=['GET'])
def get_units():
    available_only = request.args.get('available', 'false').lower() == 'true'
    query = Unit.query.join(Tower)
    
    if available_only:
        query = query.filter(Unit.is_available == True)
    
    units = query.all()
    return jsonify([{
        'id': u.id,
        'tower_name': u.tower.name,
        'unit_number': u.unit_number,
        'floor': u.floor,
        'bedrooms': u.bedrooms,
        'bathrooms': u.bathrooms,
        'area_sqft': u.area_sqft,
        'rent_amount': float(u.rent_amount),
        'is_available': u.is_available,
        'description': u.description
    } for u in units]), 200

@app.route('/api/units/<int:unit_id>', methods=['GET'])
def get_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    return jsonify({
        'id': unit.id,
        'tower_id': unit.tower_id,
        'tower_name': unit.tower.name,
        'unit_number': unit.unit_number,
        'floor': unit.floor,
        'bedrooms': unit.bedrooms,
        'bathrooms': unit.bathrooms,
        'area_sqft': unit.area_sqft,
        'rent_amount': float(unit.rent_amount),
        'is_available': unit.is_available,
        'description': unit.description
    }), 200

# API Routes - Amenities
@app.route('/api/amenities', methods=['GET'])
def get_amenities():
    amenities = Amenity.query.all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'description': a.description,
        'is_available': a.is_available,
        'icon': a.icon
    } for a in amenities]), 200

# API Routes - Bookings
@app.route('/api/bookings', methods=['POST'])
@login_required
def create_booking():
    data = request.get_json()
    
    unit = Unit.query.get(data['unit_id'])
    if not unit or not unit.is_available:
        return jsonify({'error': 'Unit not available'}), 400
    
    booking = Booking(
        user_id=session['user_id'],
        unit_id=data['unit_id'],
        move_in_date=datetime.strptime(data['move_in_date'], '%Y-%m-%d').date(),
        notes=data.get('notes')
    )
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        'message': 'Booking request submitted',
        'booking_id': booking.id
    }), 201

@app.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    user = User.query.get(session['user_id'])
    
    if user.is_admin:
        bookings = Booking.query.all()
    else:
        bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    
    return jsonify([{
        'id': b.id,
        'user_id': b.user_id,
        'username': b.user.username,
        'unit_number': b.unit.unit_number,
        'tower_name': b.unit.tower.name,
        'booking_date': b.booking_date.isoformat(),
        'move_in_date': b.move_in_date.isoformat(),
        'status': b.status,
        'notes': b.notes,
        'admin_notes': b.admin_notes
    } for b in bookings]), 200

@app.route('/api/bookings/<int:booking_id>', methods=['PATCH'])
@admin_required
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    data = request.get_json()
    
    if 'status' in data:
        booking.status = data['status']
        
        if data['status'] == 'approved':
            booking.unit.is_available = False
        elif data['status'] == 'declined':
            booking.unit.is_available = True
    
    if 'admin_notes' in data:
        booking.admin_notes = data['admin_notes']
    
    db.session.commit()
    
    return jsonify({'message': 'Booking updated', 'status': booking.status}), 200

# API Routes - Admin: Towers
@app.route('/api/towers', methods=['GET'])
def get_towers():
    towers = Tower.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'floors': t.floors,
        'description': t.description,
        'unit_count': len(t.units)
    } for t in towers]), 200

@app.route('/api/towers', methods=['POST'])
@admin_required
def create_tower():
    data = request.get_json()
    tower = Tower(
        name=data['name'],
        floors=data['floors'],
        description=data.get('description')
    )
    db.session.add(tower)
    db.session.commit()
    return jsonify({'message': 'Tower created', 'tower_id': tower.id}), 201

@app.route('/api/towers/<int:tower_id>', methods=['PUT'])
@admin_required
def update_tower(tower_id):
    tower = Tower.query.get_or_404(tower_id)
    data = request.get_json()
    
    tower.name = data.get('name', tower.name)
    tower.floors = data.get('floors', tower.floors)
    tower.description = data.get('description', tower.description)
    
    db.session.commit()
    return jsonify({'message': 'Tower updated'}), 200

@app.route('/api/towers/<int:tower_id>', methods=['DELETE'])
@admin_required
def delete_tower(tower_id):
    tower = Tower.query.get_or_404(tower_id)
    db.session.delete(tower)
    db.session.commit()
    return jsonify({'message': 'Tower deleted'}), 200

# API Routes - Admin: Units
@app.route('/api/units', methods=['POST'])
@admin_required
def create_unit():
    data = request.get_json()
    unit = Unit(
        tower_id=data['tower_id'],
        unit_number=data['unit_number'],
        floor=data['floor'],
        bedrooms=data['bedrooms'],
        bathrooms=data['bathrooms'],
        area_sqft=data.get('area_sqft'),
        rent_amount=data['rent_amount'],
        description=data.get('description')
    )
    db.session.add(unit)
    db.session.commit()
    return jsonify({'message': 'Unit created', 'unit_id': unit.id}), 201

@app.route('/api/units/<int:unit_id>', methods=['PUT'])
@admin_required
def update_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    data = request.get_json()
    
    for field in ['unit_number', 'floor', 'bedrooms', 'bathrooms', 'area_sqft', 'rent_amount', 'is_available', 'description']:
        if field in data:
            setattr(unit, field, data[field])
    
    db.session.commit()
    return jsonify({'message': 'Unit updated'}), 200

@app.route('/api/units/<int:unit_id>', methods=['DELETE'])
@admin_required
def delete_unit(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    db.session.delete(unit)
    db.session.commit()
    return jsonify({'message': 'Unit deleted'}), 200

# API Routes - Admin: Amenities
@app.route('/api/amenities', methods=['POST'])
@admin_required
def create_amenity():
    data = request.get_json()
    amenity = Amenity(
        name=data['name'],
        description=data.get('description'),
        icon=data.get('icon', 'star')
    )
    db.session.add(amenity)
    db.session.commit()
    return jsonify({'message': 'Amenity created', 'amenity_id': amenity.id}), 201

@app.route('/api/amenities/<int:amenity_id>', methods=['PUT'])
@admin_required
def update_amenity(amenity_id):
    amenity = Amenity.query.get_or_404(amenity_id)
    data = request.get_json()
    
    amenity.name = data.get('name', amenity.name)
    amenity.description = data.get('description', amenity.description)
    amenity.is_available = data.get('is_available', amenity.is_available)
    amenity.icon = data.get('icon', amenity.icon)
    
    db.session.commit()
    return jsonify({'message': 'Amenity updated'}), 200

@app.route('/api/amenities/<int:amenity_id>', methods=['DELETE'])
@admin_required
def delete_amenity(amenity_id):
    amenity = Amenity.query.get_or_404(amenity_id)
    db.session.delete(amenity)
    db.session.commit()
    return jsonify({'message': 'Amenity deleted'}), 200

# API Routes - Admin: Reports
@app.route('/api/reports/occupancy', methods=['GET'])
@admin_required
def get_occupancy_report():
    total_units = Unit.query.count()
    occupied_units = Unit.query.filter_by(is_available=False).count()
    occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
    
    return jsonify({
        'total_units': total_units,
        'occupied_units': occupied_units,
        'available_units': total_units - occupied_units,
        'occupancy_rate': round(occupancy_rate, 2)
    }), 200

@app.route('/api/reports/bookings', methods=['GET'])
@admin_required
def get_booking_report():
    total_bookings = Booking.query.count()
    pending = Booking.query.filter_by(status='pending').count()
    approved = Booking.query.filter_by(status='approved').count()
    declined = Booking.query.filter_by(status='declined').count()
    
    return jsonify({
        'total_bookings': total_bookings,
        'pending': pending,
        'approved': approved,
        'declined': declined
    }), 200

# Initialize database
@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')

@app.cli.command()
def seed_db():
    """Seed the database with sample data."""
    db.create_all()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@apartment.com',
        password_hash=generate_password_hash('admin123'),
        full_name='System Admin',
        is_admin=True
    )
    db.session.add(admin)
    
    # Create regular user
    user = User(
        username='john_doe',
        email='john@example.com',
        password_hash=generate_password_hash('password123'),
        full_name='John Doe',
        phone='1234567890'
    )
    db.session.add(user)
    
    # Create towers
    tower1 = Tower(name='Tower A', floors=10, description='Modern residential tower')
    tower2 = Tower(name='Tower B', floors=12, description='Luxury apartments')
    db.session.add_all([tower1, tower2])
    db.session.commit()
    
    # Create units
    units = [
        Unit(tower_id=tower1.id, unit_number='A101', floor=1, bedrooms=2, bathrooms=2, area_sqft=1200, rent_amount=2000),
        Unit(tower_id=tower1.id, unit_number='A201', floor=2, bedrooms=3, bathrooms=2, area_sqft=1500, rent_amount=2500),
        Unit(tower_id=tower2.id, unit_number='B101', floor=1, bedrooms=2, bathrooms=2, area_sqft=1300, rent_amount=2200),
        Unit(tower_id=tower2.id, unit_number='B301', floor=3, bedrooms=3, bathrooms=3, area_sqft=1800, rent_amount=3000),
    ]
    db.session.add_all(units)
    
    # Create amenities
    amenities = [
        Amenity(name='Swimming Pool', description='Olympic-sized pool', icon='droplet'),
        Amenity(name='Gym', description='24/7 fitness center', icon='dumbbell'),
        Amenity(name='Parking', description='Covered parking space', icon='car'),
        Amenity(name='Garden', description='Landscaped garden area', icon='flower'),
    ]
    db.session.add_all(amenities)
    
    db.session.commit()
    print('Database seeded with sample data!')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)