from app import db, app

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin', 'sponsor', 'influencer'
    sponsor = db.relationship('Sponsor', backref='user', uselist=False)
    influencer = db.relationship('Influencer', backref='user', uselist=False)
    is_admin = db.Column(db.Boolean, nullable=False, default = False)

    @property
    def password(self):
        raise AttributeError('password is not a readable property')
    
    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)
    
    
class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True)

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='influencer', lazy=True)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # 'public', 'private'
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    is_flagged = db.Column(db.Boolean, default=False , nullable=False)

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    messages = db.Column(db.Text, nullable=True)

# create database if it doesn't exist

with app.app_context():
    db.create_all()

    # Create admin if it doesn't exist
    admin = User.query.filter_by(is_admin=True).first()

    if not admin:
        # Create a new admin user
        admin = User(username='admin', email='admin@example.com', role='admin', is_admin=True)
        admin.password = 'admin'  # This will call the password setter and hash the password
        db.session.add(admin)
        db.session.commit()

    print("Admin setup complete.")