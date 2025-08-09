# Vehicle Parking Management System

A Flask-based web application for managing parking lots and vehicle parking operations.

## Project Information
- **Course**: Modern Application Development I
- **Student ID**: 23f1000968
- **Submission**: Final Milestone

## Features

### Admin Functions
- Create and manage multiple parking lots
- View real-time occupancy status
- Search parking spots by number, vehicle, or location
- Delete empty parking lots
- View all registered users

### User Functions
- User registration and login
- Book parking spots (automatic allocation)
- Release parking spots with automatic cost calculation
- View parking history
- Parking statistics dashboard

## Technology Stack
- **Backend**: Flask 3.1.1
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, Bootstrap 5.1.3, Jinja2 Templates
- **Security**: Werkzeug password hashing

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps to Run

1. Clone the repository
```bash
git clone https://github.com/23f1000968/ParkEasy.git
cd parking_app
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install flask flask-sqlalchemy
```

4. Run the application
```bash
python app.py
```

5. Access the application at `http://127.0.0.1:5000`

## Default Credentials
- **Admin Username**: admin
- **Admin Password**: admin123

## Project Structure
```
parking_app/
├── app.py                 # Main application file
├── models/
│   └── database.py       # Database models
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   └── ...
├── static/              # Static files (CSS, JS)
├── README.md
└── requirements.txt
```

## Database Schema

### Tables
1. **users**: Stores user information
2. **admins**: Admin accounts
3. **parking_lots**: Parking lot details
4. **parking_spots**: Individual parking spaces
5. **reservations**: Booking records

## API Endpoints

### Public Routes
- `/` - Home page
- `/register` - User registration
- `/user/login` - User login
- `/admin/login` - Admin login

### Admin Routes (Protected)
- `/admin/dashboard` - Admin dashboard
- `/admin/create_lot` - Create parking lot
- `/admin/view_lot/<id>` - View lot details
- `/admin/search` - Search functionality

### User Routes (Protected)
- `/user/dashboard` - User dashboard
- `/user/book_spot/<lot_id>` - Book parking
- `/user/release_spot/<id>` - Release parking
- `/user/parking_stats` - View statistics

## Key Features Implementation

### Automatic Spot Allocation
The system automatically assigns the first available spot in the selected parking lot, preventing conflicts and ensuring efficient space utilization.

### Real-time Cost Calculation
Parking costs are calculated based on:
- Duration (in hours)
- Parking lot's hourly rate
- Automatic calculation upon spot release

### Security Features
- Password hashing using Werkzeug
- Session-based authentication
- Protected routes with login requirements

## Testing the Application

1. **Admin Workflow**:
   - Login as admin
   - Create 2-3 parking lots
   - View occupancy status

2. **User Workflow**:
   - Register new account
   - Book a parking spot
   - Release spot and check cost

3. **Search Feature**:
   - Search by spot number
   - Search by vehicle number
   - Search by location name

## Future Enhancements
- Payment gateway integration
- Email notifications
- Mobile application
- Advanced analytics
- Reservation system

## License
This project is submitted as part of academic requirements for MAD-I course.
