# Insurance Portal Application

A comprehensive insurance management system built with Flask that allows users to purchase policies, file claims, and manage their insurance portfolio. The application features both user and admin interfaces with robust functionality.


## Features

### User Features
- **Account Management**: Register, login, and manage user profiles
- **Policy Management**: View, purchase, and track insurance policies
- **Quote System**: Get instant quotes for vehicle and health insurance
- **Claims Processing**: File and track insurance claims
- **Support**: Contact system for customer inquiries and support
- **Notifications**: View responses to inquiries from administrators

### Admin Features
- **Dashboard**: Overview of system statistics and recent activities
- **User Management**: View and manage user accounts
- **Contact Management**: Respond to user inquiries
- **Admin Controls**: Assign admin privileges to users

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Werkzeug security for password hashing
- **Frontend**: HTML, CSS, Bootstrap (assumed)

## Database Schema

The application uses SQLAlchemy ORM with the following models:

- **User**: Account information and authentication
- **Policy**: Insurance policy details
- **VehicleDetail**: Vehicle-specific insurance information
- **HealthDetail**: Health-specific insurance information
- **Claim**: Insurance claim information
- **Contact**: Customer support inquiries

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/insurance-portal.git
   cd insurance-portal
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application at [http://localhost:5000](http://localhost:5000)

## Usage

### Regular User

1. **Registration/Login**:
   - Register a new account or login with existing credentials
   - Regular users should use the standard login page

2. **Getting a Quote**:
   - Navigate to the quotes section
   - Select insurance type (vehicle or health)
   - Enter required details to receive an instant quote

3. **Purchasing a Policy**:
   - After receiving a quote, proceed to purchase
   - Review policy details before confirmation

4. **Filing a Claim**:
   - Navigate to the claims section
   - Select the relevant policy
   - Enter incident details and claim amount

5. **Contacting Support**:
   - Use the contact form for inquiries
   - Track responses in your profile

### Administrator

1. **Admin Login**:
   - Use the admin login page with admin credentials
   - Default admin: admin@example.com / adminpassword

2. **Dashboard**:
   - View system statistics and recent activities

3. **User Management**:
   - View all users
   - Toggle admin privileges for users

4. **Contact Management**:
   - View and respond to user inquiries
   - Mark inquiries as resolved

## Security Features

- Password hashing with Werkzeug security
- Session-based authentication
- Role-based access control
- Protection against unauthorized access

## Development

### Project Structure

```
insurance-portal/
│
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin/
│       ├── dashboard.html
│       └── ...
└── static/                # Static assets (CSS, JS, images)
    ├── css/
    ├── js/
    └── images/
```

### Database Initialization

The application automatically creates the database and an admin user on first run.

### Custom Decorators

- `login_required`: Ensures the user is logged in
- `admin_required`: Ensures the user is an admin

## License

This project is licensed under the MIT License - see the LICENSE file for details.



## Acknowledgments

- Flask and its extensions community
- Bootstrap for the frontend styling
- SQLAlchemy for the ORM functionality
