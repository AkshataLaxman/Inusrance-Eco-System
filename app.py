from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps
from random import randint
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'acko_clone_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    policies = db.relationship('Policy', backref='policyholder', lazy=True)

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_number = db.Column(db.String(20), unique=True, nullable=False)
    policy_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    premium = db.Column(db.Float, nullable=False)
    coverage_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Active')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_details = db.relationship('VehicleDetail', backref='policy', lazy=True, uselist=False)
    health_details = db.relationship('HealthDetail', backref='policy', lazy=True, uselist=False)

class VehicleDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    registration_number = db.Column(db.String(20), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)

class HealthDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    medical_history = db.Column(db.Text, nullable=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claim_number = db.Column(db.String(20), unique=True, nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)
    date_of_incident = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount_claimed = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Processing')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    policy = db.relationship('Policy', backref='claims')

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    subject = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    response = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Allow null for non-logged-in users
    user = db.relationship('User', backref='contacts')  # Add relationship

# Create database
with app.app_context():
    db.drop_all()  # Drops existing tables
    db.create_all()  # Creates new tables with updated schema
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@example.com',
            phone='1234567890',
            password=generate_password_hash('adminpassword', method='pbkdf2:sha256'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
            flash('Admin access only', 'danger')
            return redirect(url_for('admin_login'))  # Redirect to admin login instead of regular login
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = User.query.get(session['user_id']).email if 'user_id' in session else request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']
        
        contact_entry = Contact(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            user_id=session.get('user_id')
        )
        db.session.add(contact_entry)
        db.session.commit()
        
        print(f"Contact saved: ID={contact_entry.id}, User_ID={contact_entry.user_id}, Email={contact_entry.email}, Status={contact_entry.status}")
        
        flash('Message sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    user_email = User.query.get(session['user_id']).email if 'user_id' in session else ''
    print(f"Rendering contact form for user_email: {user_email}")
    return render_template('contact.html', user_email=user_email)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, phone=phone, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Regular login (non-admin only)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if user.is_admin:
                flash('Admins must use the admin login page at /admin/login', 'danger')
                return redirect(url_for('login'))
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['user_name'] = user.name
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password', 'danger')
        else:
            flash('Invalid email', 'danger')
    
    return render_template('login.html')

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email'] #admin@example.com


        password = request.form['password'] #adminpassword. 


        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if not user.is_admin:
                flash('This page is for admin login only. Please use the regular login.', 'danger')
                return redirect(url_for('admin_login'))
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['user_name'] = user.name
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid password', 'danger')
        else:
            flash('Invalid email', 'danger')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    policies = Policy.query.filter_by(user_id=user.id).all()
    claims = Claim.query.join(Policy).filter(Policy.user_id == user.id).all()
    return render_template('dashboard.html', user=user, policies=policies, claims=claims)

@app.route('/policies')
@login_required
def policies():
    user_policies = Policy.query.filter_by(user_id=session['user_id']).all()
    return render_template('policies.html', policies=user_policies)

@app.route('/policy/<int:policy_id>')
@login_required
def policy_detail(policy_id):
    policy = Policy.query.get_or_404(policy_id)
    if policy.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('policy_detail.html', policy=policy)

@app.route('/quotes')
def quotes():
    return render_template('quotes.html')

@app.route('/get_quote', methods=['GET', 'POST'])
def get_quote():
    if request.method == 'POST':
        insurance_type = request.form['insurance_type']
        if insurance_type == 'vehicle':
            return redirect(url_for('vehicle_quote'))
        elif insurance_type == 'health':
            return redirect(url_for('health_quote'))
    return render_template('get_quote.html')

@app.route('/vehicle_quote', methods=['GET', 'POST'])
def vehicle_quote():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        registration = request.form['registration']
        
        premium = float(year) * 0.01 + 5000
        
        return render_template('quote_result.html', 
                              premium=premium, 
                              insurance_type='Vehicle',
                              details={
                                  'Make': make,
                                  'Model': model,
                                  'Year': year,
                                  'Registration': registration
                              })
    
    return render_template('vehicle_quote.html')

@app.route('/health_quote', methods=['GET', 'POST'])
def health_quote():
    if request.method == 'POST':
        age = int(request.form['age'])
        gender = request.form['gender']
        medical_history = request.form.get('medical_history', '')
        
        premium = age * 100
        if medical_history:
            premium += 1000
        
        return render_template('quote_result.html', 
                              premium=premium, 
                              insurance_type='Health',
                              details={
                                  'Age': age,
                                  'Gender': gender,
                                  'Medical History': 'Yes' if medical_history else 'No'
                              })
    
    return render_template('health_quote.html')

@app.route('/buy_policy/<insurance_type>', methods=['GET', 'POST'])
@login_required
def buy_policy(insurance_type):
    if request.method == 'POST':
        try:
            policy_number = f"POL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{session['user_id']}-{randint(100, 999)}"
            start_date = datetime.now()
            end_date = datetime(start_date.year + 1, start_date.month, start_date.day)
            premium = float(request.form['premium'])
            coverage_amount = premium * 100
            
            new_policy = Policy(
                policy_number=policy_number,
                policy_type=insurance_type,
                start_date=start_date,
                end_date=end_date,
                premium=premium,
                coverage_amount=coverage_amount,
                user_id=session['user_id']
            )
            
            db.session.add(new_policy)
            db.session.commit()
            
            if insurance_type == 'Vehicle':
                vehicle_detail = VehicleDetail(
                    make=request.form['make'],
                    model=request.form['model'],
                    year=int(request.form['year']),
                    registration_number=request.form['registration'],
                    policy_id=new_policy.id
                )
                db.session.add(vehicle_detail)
            elif insurance_type == 'Health':
                health_detail = HealthDetail(
                    age=int(request.form['age']),
                    gender=request.form['gender'],
                    medical_history=request.form.get('medical_history', ''),
                    policy_id=new_policy.id
                )
                db.session.add(health_detail)
            
            db.session.commit()
            
            flash('Policy purchased successfully!', 'success')
            return redirect(url_for('policy_detail', policy_id=new_policy.id))
        
        except IntegrityError:
            db.session.rollback()
            flash('Error: Unable to generate a unique policy number. Please try again.', 'danger')
            return redirect(url_for('buy_policy', insurance_type=insurance_type))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('buy_policy', insurance_type=insurance_type))
    
    return render_template('buy_policy.html', insurance_type=insurance_type)

@app.route('/claims')
@login_required
def claims():
    user_claims = Claim.query.join(Policy).filter(Policy.user_id == session['user_id']).all()
    return render_template('claims.html', claims=user_claims)

@app.route('/file_claim', methods=['GET', 'POST'])
@login_required
def file_claim():
    user_policies = Policy.query.filter_by(user_id=session['user_id'], status='Active').all()
    
    if request.method == 'POST':
        policy_id = request.form['policy_id']
        date_of_incident = datetime.strptime(request.form['date_of_incident'], '%Y-%m-%d')
        description = request.form['description']
        amount_claimed = float(request.form['amount_claimed'])
        
        claim_number = f"CLM-{datetime.now().strftime('%Y%m%d')}-{policy_id}"
        
        new_claim = Claim(
            claim_number=claim_number,
            policy_id=policy_id,
            date_of_incident=date_of_incident,
            description=description,
            amount_claimed=amount_claimed
        )
        
        db.session.add(new_claim)
        db.session.commit()
        
        flash('Claim filed successfully!', 'success')
        return redirect(url_for('claims'))
    
    return render_template('file_claim.html', policies=user_policies)

@app.route('/claim/<int:claim_id>')
@login_required
def claim_detail(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    if claim.policy.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('claim_detail.html', claim=claim)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    contacts_with_response = Contact.query.filter_by(user_id=user.id).filter(
        Contact.response.isnot(None),
        Contact.status == 'Resolved'
    ).order_by(Contact.submitted_at.desc()).all()
    
    print(f"Profile for User ID: {user.id}, Email: {user.email}")
    print(f"Found {len(contacts_with_response)} resolved contacts:")
    for contact in contacts_with_response:
        print(f" - ID={contact.id}, Subject={contact.subject}, Response={contact.response}, Status={contact.status}, User_ID={contact.user_id}")
    
    return render_template('profile.html', user=user, contacts=contacts_with_response)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.name = request.form['name']
        user.phone = request.form['phone']
        
        if request.form['new_password']:
            if not check_password_hash(user.password, request.form['current_password']):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('edit_profile'))
            
            user.password = generate_password_hash(request.form['new_password'], method='pbkdf2:sha256')
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user)

# Admin Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_policies = Policy.query.count()
    total_claims = Claim.query.count()
    pending_contacts = Contact.query.filter_by(status='Pending').count()
    active_policies = Policy.query.filter_by(status='Active').count()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_contacts = Contact.query.order_by(Contact.submitted_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_policies=total_policies,
                         total_claims=total_claims,
                         pending_contacts=pending_contacts,
                         active_policies=active_policies,
                         recent_users=recent_users,
                         recent_contacts=recent_contacts)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/contacts')
@admin_required
def admin_contacts():
    contacts = Contact.query.order_by(Contact.submitted_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/contact/<int:contact_id>', methods=['GET', 'POST'])
@admin_required
def admin_contact_detail(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    
    if request.method == 'POST':
        contact.status = request.form['status']
        contact.response = request.form['response']
        db.session.commit()
        print(f"Contact updated: ID={contact.id}, User_ID={contact.user_id}, Status={contact.status}, Response={contact.response}")
        flash('Contact updated successfully', 'success')
        return redirect(url_for('admin_contacts'))
    
    print(f"Viewing contact: ID={contact.id}, User_ID={contact.user_id}, Status={contact.status}, Response={contact.response}")
    return render_template('admin/contact_detail.html', contact=contact)

@app.route('/admin/toggle_admin/<int:user_id>')
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'User admin status updated', 'success')
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')