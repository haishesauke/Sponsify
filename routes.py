from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, session
from app import app, db
from models import User, Campaign, Sponsor, Influencer, AdRequest
from datetime import datetime
def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner
@app.route('/')
@auth_required
def index():
    return render_template('index.html')

@app.route('/login')

def login():   
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Validate and authenticate user
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        flash('Invalid username or password')
        return redirect(url_for('login'))
    
    # Login successful
    session['user_id'] = user.id
    session['user_role'] = user.role  # Store user role in session
    session['logged_in'] = True

    # Redirect based on the user role
    if user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user.role == 'sponsor':
        return redirect(url_for('sponsor_dashboard'))
    elif user.role == 'influencer':
        return redirect(url_for('influencer_dashboard'))
    
    # Default redirection (if role is undefined or something else)
    return redirect(url_for('index'))


@app.route('/logout')

def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))



@app.route('/register' )   

def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    role = request.form.get('role')

    # check if username, email, or password field is empty
    if not username or not email or not password:
        flash('Please fill all the fields')
        return redirect(url_for('register'))
    
    # check if email already exists
    if User.query.filter_by(email=email).first():
        flash('Email already exists')
        return redirect(url_for('register'))

    # check if username already exists
    if User.query.filter_by(username=username).first():
        flash('Username already exists')
        return redirect(url_for('register'))
    
    # check if password and confirm password match
    if password!= confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('register'))
    
    # Create the user and set the password using the setter
    user = User(username=username, email=email, role=role)
    user.password = password  # This uses the setter method to hash the password
    db.session.add(user)
    db.session.commit()

    flash('Registration successful! Please log in.')
    session['user_id'] = user.id
    # return redirect(url_for('login'))
    if role == 'sponsor':
        return redirect(url_for('sponsor_registration'))
    elif role == 'influencer':
        return redirect(url_for('influencer_registration'))


@app.route('/sponsor_registration')
def register_sponsor():
    return render_template('register_spn.html')


@app.route('/sponsor_registration', methods=['POST'])
def sponsor_registration():
    company_name = request.form.get('company_name')
    industry = request.form.get('industry')
    budget = request.form.get('budget')
    user_id = session.get('user_id')
    if not company_name or not industry or not budget:
        flash('Please fill all the fields')
        return redirect(url_for('sponsor_registration'))
    
    sponsor = Sponsor(company_name=company_name, industry=industry, budget=budget, user_id= user_id)
    db.session.add(sponsor)
    db.session.commit()
    flash('Sponsor registration successful')
    session.pop('user_id', None)
    return redirect(url_for('login'))
    
@app.route('/influencer_registration')

def register_influencer():
    return render_template('register_inf.html')

@app.route('/influencer_registration', methods=['POST'])
def influencer_registration():
    name = request.form.get('name')
    category = request.form.get('category')
    niche = request.form.get('niche')
    reach = request.form.get('reach')
    user_id = session.get('user_id')
    print(f"Name: {name}, Category: {category}, Niche: {niche}, Reach: {reach}")
    if not name or not category or not niche or not reach:
        flash('Please fill all the fields')
        return redirect(url_for('register_influencer'))
    
    influencer = Influencer(name=name, category = category , niche = niche, reach = reach ,user_id=user_id)
    db.session.add(influencer)
    db.session.commit()
    flash('Influencer registration successful')
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
@auth_required
def admin_dashboard():
    # fetch add requests
    ad_requests = AdRequest.query.all()
    # Fetch total campaigns and split between public and private
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()

    # fetch flagged campaigns

    flagged_campaigns = Campaign.query.filter_by(is_flagged=True).count()


    # Fetch total ad requests and their statuses
    total_ad_requests = AdRequest.query.count()
    pending_ad_requests = AdRequest.query.filter_by(status='Pending').count()
    accepted_ad_requests = AdRequest.query.filter_by(status='Accepted').count()

    # Fetch total active users (you can define 'active' as necessary)
    active_users = User.query.filter_by(is_active=True).count()


    # Fetch all campaigns for listing
    campaigns = Campaign.query.all()

    return render_template('admin.html', 
                           total_campaigns=total_campaigns,
                           ad_requests=ad_requests,
                           flagged_campaigns=flagged_campaigns, 
                           public_campaigns=public_campaigns, 
                           private_campaigns=private_campaigns,
                           total_ad_requests=total_ad_requests,
                           pending_ad_requests=pending_ad_requests,
                           accepted_ad_requests=accepted_ad_requests,
                           active_users=active_users,
                           campaigns=campaigns)


@app.route('/flag_campaign/<int:campaign_id>', methods=['POST'])
@auth_required
def flag_campaign(campaign_id):


    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))

    campaign = Campaign.query.get(campaign_id)
    if campaign:
        campaign.is_flagged = True
        db.session.commit()
        flash('Campaign flagged as inappropriate')
    else:
        flash('Campaign not found')

    return redirect(url_for('admin_dashboard'))

@app.route('/sponsor_dashboard')
@auth_required
def sponsor_dashboard():
    sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()
    if not sponsor:
        flash('You must complete sponsor registration first.')
        return redirect(url_for('sponsor_registration'))
    
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    return render_template('sponsor.html', sponsor=sponsor, campaigns=campaigns)

@app.route('/influencer_dashboard')
@auth_required
def influencer_dashboard():
    influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
    if not influencer:
        flash('You must complete influencer registration first.')
        return redirect(url_for('register_influencer'))
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()

    # Render the dashboard and pass the ad requests
    return render_template('influencer.html', influencer=influencer, ad_requests=ad_requests)



@app.route('/update_influencer_profile')
@auth_required
def update_influencer_profile():
    influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
    return render_template('/update_influencer_profile.html', influencer = influencer)

@app.route('/update_influencer_profile', methods=['POST'])
@auth_required
def update_influencer_profile_post():
    influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
    name = request.form.get('name')
    category = request.form.get('category')
    niche = request.form.get('niche')
    reach = request.form.get('reach')
    
    if name == '' or category == '' or niche == '' or reach == '':
        flash('Please fill all the fields.')
        return redirect(url_for('update_influencer_profile'))
    
    influencer.name = name
    influencer.category = category
    influencer.niche = niche
    influencer.reach = reach

    db.session.commit()
    flash('Influencer profile updated successfully.')
    return redirect(url_for('influencer_dashboard'))



@app.route('/create_campaign', methods=['POST'])
@auth_required
def create_campaign():
    name = request.form.get('name')
    description = request.form.get('description')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    budget = request.form.get('budget')
    visibility = request.form.get('visibility')
    
    sponsor = Sponsor.query.filter_by(user_id=session['user_id']).first()

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    if not sponsor:
        flash('You must complete sponsor registration first.')
        return redirect(url_for('sponsor_registration'))
    
    if not name or not description or not start_date or not end_date or not budget or not visibility:
        flash('Please fill all the fields.')
        return redirect(url_for('sponsor_dashboard'))

    campaign = Campaign(name=name, description=description, start_date=start_date, end_date=end_date,  budget=budget,  visibility=visibility, sponsor_id=sponsor.id)
    db.session.add(campaign)
    db.session.commit()
    flash('Campaign created successfully!')
    return redirect(url_for('sponsor_dashboard'))


@app.route('/campaigns/edit/<int:campaign_id>', methods=['GET','POST'])
@auth_required
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    # Check if the sponsor is the owner of the campaign
    # if campaign.sponsor_id != session['user_id']:
    #     flash('Unauthorized action')
    #     return redirect(url_for('sponsor_dashboard'))

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = start_date
        campaign.end_date = end_date
        campaign.budget = request.form['budget']
        campaign.visibility = request.form['visibility']

        db.session.commit()
        flash('Campaign updated successfully')
        return redirect(url_for('sponsor_dashboard'))

    return render_template('edit_campaign.html', campaign=campaign)


@app.route('/campaigns/delete/<int:campaign_id>', methods=['POST'])
@auth_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    # # Check if the sponsor is the owner of the campaign
    # if campaign.sponsor_id != session['user_id']:
    #     flash('Unauthorized action')
    #     return redirect(url_for('sponsor_dashboard'))

    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully')
    return redirect(url_for('sponsor_dashboard'))

#create view influencers route
# @app.route('/view_influencers')
# @auth_required

# def view_influencers():
#     influencer = Influencer.query.all()
#     print(influencer)
#     return render_template('view_influencers.html', influencer=influencer)

# View Influencers for a Specific Campaign
@app.route('/campaign/<int:campaign_id>/select_influencers')
@auth_required
def select_influencers(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    influencers = Influencer.query.all()  # Fetch all influencers
    return render_template('view_influencers.html', campaign=campaign, influencers=influencers)

@app.route('/campaign/<int:campaign_id>/send_ad_request/<int:influencer_id>')
@auth_required
def show_ad_request_form(campaign_id, influencer_id):
    # Fetch the campaign and influencer details
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer = Influencer.query.get_or_404(influencer_id)

    # Render the form to send ad request
    return render_template('ad_request_form.html', campaign=campaign, influencer=influencer)


@app.route('/campaign/<int:campaign_id>/send_ad_request/<int:influencer_id>', methods=['POST'])
@auth_required
def submit_ad_request(campaign_id, influencer_id):
    # Fetch the campaign and influencer details
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer = Influencer.query.get_or_404(influencer_id)

    # Get the form data
    requirements = request.form['requirements']
    payment_amount = float(request.form['payment_amount'])

    # Create a new AdRequest
    ad_request = AdRequest(
        campaign_id=campaign.id,
        influencer_id=influencer.id,
        requirements=requirements,
        payment_amount=payment_amount,
        status='Pending'
    )
    db.session.add(ad_request)
    db.session.commit()

    flash('Ad request sent successfully!', 'success')
    return redirect(url_for('select_influencers', campaign_id=campaign.id))


@app.route('/ad_request/<int:ad_request_id>/accept', methods=['POST'])
@auth_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    # Ensure the logged-in influencer is the one who received the request
    influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
    if ad_request.influencer_id != influencer.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('influencer_dashboard'))

    ad_request.status = 'Accepted'
    db.session.commit()

    flash('Ad request accepted successfully!', 'success')
    return redirect(url_for('influencer_dashboard'))

@app.route('/ad_request/<int:ad_request_id>/reject', methods=['POST'])
@auth_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    # Ensure the logged-in influencer is the one who received the request
    influencer = Influencer.query.filter_by(user_id=session['user_id']).first()
    if ad_request.influencer_id != influencer.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('influencer_dashboard'))

    ad_request.status = 'Rejected'
    db.session.commit()

    flash('Ad request rejected.', 'warning')
    return redirect(url_for('influencer_dashboard'))

@app.route('/admin/ad_request/<int:request_id>/status/<string:new_status>', methods=['POST'])
@auth_required
def change_ad_request_status(request_id, new_status):
    # Fetch the ad request by its ID
    ad_request = AdRequest.query.get_or_404(request_id)

    # Validate new status
    if new_status not in ['Accepted', 'Rejected']:
        flash('Invalid status provided', 'danger')
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

    # Update the status
    ad_request.status = new_status
    db.session.commit()

    # Provide feedback to the admin
    flash(f'Ad request {ad_request.id} has been {new_status.lower()}.', 'success')
    
    return redirect(url_for('admin_dashboard'))  # Redirect back to the dashboard

