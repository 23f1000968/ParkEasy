# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.database import db, User, Admin, ParkingLot, ParkingSpot, Reservation, init_db
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Make datetime available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

# Create database tables
with app.app_context():
    db.create_all()
    init_db(app)

# Helper function to check if user is logged in
def is_logged_in():
    return 'user_id' in session or 'admin_id' in session

def is_admin():
    return 'admin_id' in session

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('user_login'))
    
    return render_template('register.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = 'user'
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('user_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['username'] = admin.username
            session['user_type'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    """Logout user or admin"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not is_admin():
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    # Get all parking lots with their statistics
    parking_lots = ParkingLot.query.all()
    lot_stats = []
    
    for lot in parking_lots:
        total_spots = len(lot.spots)
        occupied_spots = sum(1 for spot in lot.spots if spot.status == 'O')
        available_spots = total_spots - occupied_spots
        
        lot_stats.append({
            'lot': lot,
            'total_spots': total_spots,
            'occupied_spots': occupied_spots,
            'available_spots': available_spots
        })
    
    # Get all users
    users = User.query.all()
    
    return render_template('admin_dashboard.html', lot_stats=lot_stats, users=users)

@app.route('/admin/create_lot', methods=['GET', 'POST'])
def create_lot():
    """Create new parking lot"""
    if not is_admin():
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        price = float(request.form.get('price'))
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        max_spots = int(request.form.get('max_spots'))
        
        # Create parking lot
        new_lot = ParkingLot(
            prime_location_name=name,
            price_per_hour=price,
            address=address,
            pin_code=pin_code,
            maximum_spots=max_spots
        )
        db.session.add(new_lot)
        db.session.commit()
        
        # Create parking spots for this lot
        for i in range(1, max_spots + 1):
            spot = ParkingSpot(lot_id=new_lot.id, spot_number=i)
            db.session.add(spot)
        db.session.commit()
        
        flash(f'Parking lot "{name}" created with {max_spots} spots!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_lot.html')

@app.route('/admin/view_lot/<int:lot_id>')
def view_lot_details(lot_id):
    """View detailed parking lot information"""
    if not is_admin():
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    # Get current reservations for occupied spots
    spot_details = []
    for spot in spots:
        if spot.status == 'O':
            reservation = Reservation.query.filter_by(
                spot_id=spot.id, 
                is_active=True
            ).first()
            spot_details.append({
                'spot': spot,
                'reservation': reservation
            })
        else:
            spot_details.append({
                'spot': spot,
                'reservation': None
            })
    
    return render_template('view_lot_details.html', lot=lot, spot_details=spot_details)

@app.route('/user/dashboard')
def user_dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    
    # Get user's active reservation
    active_reservation = Reservation.query.filter_by(
        user_id=user_id, 
        is_active=True
    ).first()
    
    # Get user's parking history
    past_reservations = Reservation.query.filter_by(
        user_id=user_id, 
        is_active=False
    ).order_by(Reservation.leaving_timestamp.desc()).limit(10).all()
    
    # Get available parking lots
    parking_lots = []
    for lot in ParkingLot.query.all():
        available_spots = sum(1 for spot in lot.spots if spot.status == 'A')
        if available_spots > 0:
            parking_lots.append({
                'lot': lot,
                'available_spots': available_spots
            })
    
    return render_template('user_dashboard.html', 
                         active_reservation=active_reservation,
                         past_reservations=past_reservations,
                         parking_lots=parking_lots)

@app.route('/user/book_spot/<int:lot_id>', methods=['POST'])
def book_spot(lot_id):
    """Book a parking spot"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    vehicle_number = request.form.get('vehicle_number')
    
    # Check if user already has an active reservation
    existing = Reservation.query.filter_by(user_id=user_id, is_active=True).first()
    if existing:
        flash('You already have an active parking reservation!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Find first available spot in the lot
    available_spot = ParkingSpot.query.filter_by(
        lot_id=lot_id, 
        status='A'
    ).first()
    
    if not available_spot:
        flash('No available spots in this parking lot!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Create reservation
    reservation = Reservation(
        spot_id=available_spot.id,
        user_id=user_id,
        vehicle_number=vehicle_number
    )
    
    # Update spot status
    available_spot.status = 'O'
    
    db.session.add(reservation)
    db.session.commit()
    
    flash(f'Spot {available_spot.spot_number} booked successfully!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/user/release_spot/<int:reservation_id>')
def release_spot(reservation_id):
    """Release a parking spot"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('user_login'))
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Verify this reservation belongs to the logged-in user
    if reservation.user_id != session['user_id']:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Calculate parking duration and cost
    reservation.leaving_timestamp = datetime.utcnow()
    duration_hours = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
    reservation.total_cost = round(duration_hours * reservation.spot.lot.price_per_hour, 2)
    reservation.is_active = False
    
    # Free up the spot
    reservation.spot.status = 'A'
    
    db.session.commit()
    
    flash(f'Parking spot released! Total cost: ₹{reservation.total_cost}', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/admin/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    """Delete a parking lot"""
    if not is_admin():
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spots are occupied
    occupied_spots = sum(1 for spot in lot.spots if spot.status == 'O')
    if occupied_spots > 0:
        flash('Cannot delete parking lot with occupied spots!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Get all spot IDs for this lot
    spot_ids = [spot.id for spot in lot.spots]
    
    # Delete all reservations associated with these spots
    if spot_ids:
        Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).delete(synchronize_session=False)

    db.session.delete(lot)
    db.session.commit()
    
    flash(f'Parking lot "{lot.prime_location_name}" deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    """Search for parking spots"""
    if not is_admin():
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    search_results = None
    search_query = ''
    search_type = None
    
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        search_query = request.form.get('search_query', '').strip()
        
        try:
            if search_type == 'spot_number' and search_query.isdigit():
                # Search by spot number
                search_results = db.session.query(ParkingSpot, ParkingLot).join(
                    ParkingLot, ParkingSpot.lot_id == ParkingLot.id
                ).filter(ParkingSpot.spot_number == int(search_query)).all()
                
            elif search_type == 'vehicle' and search_query:
                # Search by vehicle number
                search_results = db.session.query(Reservation, ParkingSpot, ParkingLot, User).join(
                    ParkingSpot, Reservation.spot_id == ParkingSpot.id
                ).join(
                    ParkingLot, ParkingSpot.lot_id == ParkingLot.id
                ).join(
                    User, Reservation.user_id == User.id
                ).filter(
                    Reservation.vehicle_number.contains(search_query),
                    Reservation.is_active == True
                ).all()
                
            elif search_type == 'location' and search_query:
                # Search by location name
                search_results = ParkingLot.query.filter(
                    ParkingLot.prime_location_name.contains(search_query)
                ).all()
            else:
                flash('Please enter a valid search query', 'error')
                
        except Exception as e:
            flash(f'Search error: {str(e)}', 'error')
            search_results = None
    
    return render_template('admin_search.html', 
                         search_results=search_results, 
                         search_query=search_query,
                         search_type=search_type)

@app.route('/user/parking_stats')
def user_parking_stats():
    """Show user's parking statistics"""
    if 'user_id' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    
    # Get all user's reservations
    all_reservations = Reservation.query.filter_by(user_id=user_id, is_active=False).all()
    
    # Calculate statistics
    total_parkings = len(all_reservations)
    total_cost = sum(r.total_cost for r in all_reservations)
    total_hours = sum(
        (r.leaving_timestamp - r.parking_timestamp).total_seconds() / 3600 
        for r in all_reservations if r.leaving_timestamp
    )
    
    # Most used parking lot
    lot_usage = {}
    for r in all_reservations:
        lot_name = r.spot.lot.prime_location_name
        lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
    
    favorite_lot = max(lot_usage.items(), key=lambda x: x[1])[0] if lot_usage else None
    
    stats = {
        'total_parkings': total_parkings,
        'total_cost': round(total_cost, 2),
        'total_hours': round(total_hours, 1),
        'average_cost': round(total_cost / total_parkings, 2) if total_parkings > 0 else 0,
        'average_duration': round(total_hours / total_parkings, 1) if total_parkings > 0 else 0,
        'favorite_lot': favorite_lot
    }
    
    return render_template('user_stats.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
