# Residential Apartment Rental Portal

A full-stack web application for managing apartment rentals with user and admin portals.

## Features

### User Portal
- User registration and authentication
- Browse available apartments
- View detailed unit information
- Request apartment bookings
- Track booking status
- View amenities

### Admin Portal
- Dashboard with occupancy statistics
- Manage towers and units
- Approve/decline booking requests
- Manage amenities
- View booking reports
- Track occupancy rates

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Deployment**: Docker & Docker Compose

## Project Structure

```
apartment-rental-portal/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── README.md             # This file
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── register.html     # Registration page
    ├── login.html        # Login page
    ├── browse.html       # Browse flats page
    └── admin.html        # Admin dashboard
```

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Git (optional)

### Installation

1. **Create project directory and files**

```bash
mkdir apartment-rental-portal
cd apartment-rental-portal
```

2. **Create all necessary files**

Create the following files with their respective content:
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker Compose configuration
- `templates/` directory with all HTML files

3. **Build and run with Docker**

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

4. **Access the application**

- **User Portal**: http://localhost:5000
- **Admin Portal**: http://localhost:5000/admin

### Demo Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**User Account:**
- Username: `john_doe`
- Password: `password123`

## Docker Commands

```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build

# Access database
docker exec -it apartment_db psql -U postgres -d apartment_rental

# Reset database (WARNING: Deletes all data)
docker-compose down -v
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `POST /api/logout` - Logout user
- `GET /api/me` - Get current user info

### Units
- `GET /api/units` - List all units
- `GET /api/units/<id>` - Get unit details
- `POST /api/units` - Create unit (Admin)
- `PUT /api/units/<id>` - Update unit (Admin)
- `DELETE /api/units/<id>` - Delete unit (Admin)

### Bookings
- `GET /api/bookings` - List bookings
- `POST /api/bookings` - Create booking
- `PATCH /api/bookings/<id>` - Update booking status (Admin)

### Towers
- `GET /api/towers` - List towers
- `POST /api/towers` - Create tower (Admin)
- `PUT /api/towers/<id>` - Update tower (Admin)
- `DELETE /api/towers/<id>` - Delete tower (Admin)

### Amenities
- `GET /api/amenities` - List amenities
- `POST /api/amenities` - Create amenity (Admin)
- `PUT /api/amenities/<id>` - Update amenity (Admin)
- `DELETE /api/amenities/<id>` - Delete amenity (Admin)

### Reports
- `GET /api/reports/occupancy` - Occupancy statistics (Admin)
- `GET /api/reports/bookings` - Booking statistics (Admin)

## Database Schema

### Tables
- **users** - User accounts and authentication
- **towers** - Building/tower information
- **units** - Individual apartment units
- **amenities** - Available amenities
- **bookings** - Booking requests
- **leases** - Active leases
- **payments** - Payment records (mock data)

## Development

### Running without Docker

1. **Install PostgreSQL**

2. **Create database**
```sql
CREATE DATABASE apartment_rental;
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
export DATABASE_URL=postgresql://postgres:password@localhost:5432/apartment_rental
export SECRET_KEY=your-secret-key
```

5. **Initialize database**
```bash
flask init-db
flask seed-db
```

6. **Run application**
```bash
python app.py
```

## Features Implemented

✅ User registration and authentication
✅ JWT-like session management
✅ Browse available apartments with filters
✅ Booking request system
✅ Admin dashboard with statistics
✅ Tower and unit management
✅ Amenity management
✅ Booking approval workflow
✅ Occupancy tracking
✅ Responsive design with Tailwind CSS
✅ PostgreSQL database integration
✅ Docker containerization
✅ REST API architecture

## Future Enhancements

- Payment gateway integration
- Email notifications
- Document upload for lease agreements
- Maintenance request system
- Tenant portal for current residents
- Advanced search and filtering
- Photo gallery for units
- Calendar view for move-in dates
- SMS notifications
- Reviews and ratings

## Troubleshooting

### Database connection issues
```bash
# Check if database is running
docker-compose ps

# Restart services
docker-compose restart
```

### Port already in use
```bash
# Change ports in docker-compose.yml
ports:
  - "5001:5000"  # Use different port
```

### Permission issues
```bash
# Fix permissions
sudo chown -R $USER:$USER .
```

## License

This project is created for educational purposes.

## Support

For issues or questions, please check the application logs:
```bash
docker-compose logs web
```