from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import User, Listing, Payment
from werkzeug.security import generate_password_hash
import logging
import requests
import os
import hmac
import hashlib
import json

@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'farmer')
        
        if not all([name, email, password]):
            flash('Please fill in all fields.', 'error')
            return render_template('login.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login instead.', 'error')
            return render_template('login.html')
        
        # Create new user
        new_user = User()
        new_user.name = name
        new_user.email = email
        new_user.role = role
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            session['user_name'] = new_user.name
            session['user_role'] = new_user.role
            
            flash(f'Registration successful! Welcome, {new_user.name}!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard route"""
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    user_role = session.get('user_role', 'farmer')
    
    if user_role == 'buyer':
        return redirect(url_for('buyer_dashboard'))
    else:
        return redirect(url_for('farmer_dashboard'))

@app.route('/farmer_dashboard')
def farmer_dashboard():
    """Farmer dashboard route"""
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_name = session['user_name']
    
    # Get user's listings
    listings = Listing.query.filter_by(supplier_id=user_id).order_by(Listing.created_at.desc()).all()
    
    return render_template('dashboard.html', user_name=user_name, listings=listings)

@app.route('/buyer_dashboard')
def buyer_dashboard():
    """Buyer dashboard route"""
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '')
    
    # Get all available listings with farmer names
    query = db.session.query(Listing, User).join(User, Listing.supplier_id == User.id).filter(Listing.is_available == True)
    
    if search_query:
        query = query.filter(Listing.item_name.ilike(f'%{search_query}%'))
    
    listings_with_farmers = query.order_by(Listing.created_at.desc()).all()
    
    return render_template('buyer_dashboard.html', 
                         user_name=session['user_name'], 
                         listings_with_farmers=listings_with_farmers,
                         search_query=search_query)

@app.route('/create_listing', methods=['POST'])
def create_listing():
    """Create a new listing"""
    if 'user_id' not in session:
        flash('Please login to create a listing.', 'error')
        return redirect(url_for('login'))
    
    item_name = request.form.get('item_name')
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    currency = request.form.get('currency')
    contact = request.form.get('contact')
    is_available = request.form.get('is_available') == 'on'
    
    if not all([item_name, quantity, contact]):
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('dashboard'))
    
    new_listing = Listing()
    new_listing.item_name = item_name
    new_listing.quantity = quantity
    new_listing.price = float(price) if price else None
    new_listing.currency = currency if currency else 'USD'
    new_listing.contact = contact
    new_listing.is_available = is_available
    new_listing.supplier_id = session['user_id']
    
    try:
        db.session.add(new_listing)
        db.session.commit()
        flash('Listing created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating listing: {str(e)}")
        flash('Failed to create listing. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/update_listing/<listing_id>', methods=['POST'])
def update_listing(listing_id):
    """Update an existing listing"""
    if 'user_id' not in session:
        flash('Please login to update listings.', 'error')
        return redirect(url_for('login'))
    
    listing = Listing.query.filter_by(id=listing_id, supplier_id=session['user_id']).first()
    
    if not listing:
        flash('Listing not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('dashboard'))
    
    listing.item_name = request.form.get('item_name', listing.item_name)
    listing.quantity = request.form.get('quantity', listing.quantity)
    price = request.form.get('price')
    listing.price = float(price) if price else listing.price
    listing.currency = request.form.get('currency', listing.currency)
    listing.contact = request.form.get('contact', listing.contact)
    listing.is_available = request.form.get('is_available') == 'on'
    
    try:
        db.session.commit()
        flash('Listing updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating listing: {str(e)}")
        flash('Failed to update listing. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_listing/<listing_id>', methods=['POST'])
def delete_listing(listing_id):
    """Delete a listing"""
    if 'user_id' not in session:
        flash('Please login to delete listings.', 'error')
        return redirect(url_for('login'))
    
    listing = Listing.query.filter_by(id=listing_id, supplier_id=session['user_id']).first()
    
    if not listing:
        flash('Listing not found or you do not have permission to delete it.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(listing)
        db.session.commit()
        flash('Listing deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting listing: {str(e)}")
        flash('Failed to delete listing. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('500.html'), 500

# Paystack Payment Integration Endpoints

@app.route('/paystack/initiate', methods=['POST'])
def paystack_initiate():
    """
    Initialize Paystack payment transaction
    Security: Validates user session, sanitizes inputs, uses HTTPS
    """
    # Verify user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        # Validate required fields
        required_fields = ['listing_id', 'amount', 'currency']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        listing_id = data['listing_id']
        amount = float(data['amount'])
        currency = data['currency'].upper()
        
        # Security: Validate amount is positive
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Security: Validate currency
        valid_currencies = ['USD', 'EUR', 'CAD', 'GHS', 'NGN']
        if currency not in valid_currencies:
            return jsonify({'error': 'Unsupported currency'}), 400
        
        # Get buyer information
        buyer = User.query.get(session['user_id'])
        if not buyer:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify listing exists and is available
        listing_query = db.session.query(Listing, User).join(User, Listing.supplier_id == User.id)
        listing_data = listing_query.filter(Listing.id == listing_id, Listing.is_available == True).first()
        
        if not listing_data:
            return jsonify({'error': 'Listing not found or no longer available'}), 404
        
        listing, supplier = listing_data
        
        # Security: Prevent self-purchase
        if listing.supplier_id == session['user_id']:
            return jsonify({'error': 'Cannot purchase your own listing'}), 400
        
        # Convert amount to kobo (Paystack uses smallest currency unit)
        amount_in_kobo = int(amount * 100)
        
        # Prepare Paystack request
        paystack_url = "https://api.paystack.co/transaction/initialize"
        
        # Generate unique reference
        import uuid
        reference = f"fb_{uuid.uuid4().hex[:12]}"
        
        headers = {
            'Authorization': f'Bearer {os.environ.get("PAYSTACK_SECRET_KEY")}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'amount': amount_in_kobo,
            'currency': currency,
            'email': buyer.email,
            'reference': reference,
            'callback_url': f"{request.url_root.rstrip('/')}payment/success",
            'metadata': {
                'listing_id': str(listing_id),
                'buyer_id': str(session['user_id']),
                'supplier_id': str(listing.supplier_id),
                'item_name': listing.item_name
            }
        }
        
        # Create payment record with pending status
        payment = Payment()
        payment.amount = amount
        payment.currency = currency
        payment.status = 'pending'
        payment.transaction_id = reference
        payment.supplier_id = listing.supplier_id
        payment.buyer_id = session['user_id']
        payment.listing_id = listing_id
        
        db.session.add(payment)
        db.session.commit()
        
        # Make request to Paystack
        response = requests.post(paystack_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            paystack_data = response.json()
            if paystack_data['status']:
                return jsonify({
                    'status': 'success',
                    'authorization_url': paystack_data['data']['authorization_url'],
                    'reference': reference
                })
            else:
                # Update payment status to failed
                payment.status = 'failed'
                db.session.commit()
                return jsonify({'error': paystack_data.get('message', 'Payment initialization failed')}), 400
        else:
            # Update payment status to failed
            payment.status = 'failed'
            db.session.commit()
            logging.error(f"Paystack API error: {response.status_code} - {response.text}")
            return jsonify({'error': 'Payment service unavailable'}), 503
            
    except ValueError as e:
        logging.error(f"Value error in payment initiation: {str(e)}")
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error initiating payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/payment/success')
def payment_success():
    """
    Handle Paystack callback after payment
    Extract reference and redirect to transaction status page
    """
    try:
        # Get transaction reference from URL parameters
        reference = request.args.get('reference')
        if not reference:
            flash('Invalid payment reference.', 'error')
            return redirect(url_for('buyer_dashboard'))
        
        # Query database for transaction record
        payment = Payment.query.filter_by(transaction_id=reference).first()
        if not payment:
            flash('Transaction not found.', 'error')
            return redirect(url_for('buyer_dashboard'))
        
        # Redirect to transaction status page
        return redirect(url_for('transaction_status', reference=reference))
        
    except Exception as e:
        logging.error(f"Error in payment callback: {str(e)}")
        flash('Error processing payment callback.', 'error')
        return redirect(url_for('buyer_dashboard'))

@app.route('/transactions/<reference>')
def transaction_status(reference):
    """
    Display transaction status page with polling for pending payments
    """
    try:
        # Security: Check if user is logged in
        if 'user_id' not in session:
            flash('Please log in to view transactions.', 'error')
            return redirect(url_for('login'))
        
        # Find the payment record
        payment = Payment.query.filter_by(transaction_id=reference).first()
        if not payment:
            flash('Transaction not found.', 'error')
            return redirect(url_for('buyer_dashboard'))
        
        # Security: Verify user owns this transaction
        if payment.buyer_id != session['user_id']:
            flash('Access denied.', 'error')
            return redirect(url_for('buyer_dashboard'))
        
        # Get associated listing and supplier info
        listing_query = db.session.query(Listing, User).join(User, Listing.supplier_id == User.id)
        listing_data = listing_query.filter(Listing.id == payment.listing_id).first()
        
        if not listing_data:
            flash('Associated listing not found.', 'error')
            return redirect(url_for('buyer_dashboard'))
        
        listing, supplier = listing_data
        
        # Prepare transaction details
        transaction_details = {
            'reference': payment.transaction_id,
            'status': payment.status,
            'amount': payment.amount,
            'currency': payment.currency,
            'item_name': listing.item_name,
            'supplier_name': supplier.name,
            'created_at': payment.created_at,
            'updated_at': payment.updated_at
        }
        
        return render_template('transaction_status.html', 
                             transaction=transaction_details,
                             listing=listing,
                             supplier=supplier)
        
    except Exception as e:
        logging.error(f"Error displaying transaction status: {str(e)}")
        flash('Error loading transaction details.', 'error')
        return redirect(url_for('buyer_dashboard'))

@app.route('/api/transaction-status/<reference>')
def api_transaction_status(reference):
    """
    API endpoint for polling transaction status
    Returns JSON for AJAX requests
    """
    try:
        # Security: Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Find the payment record
        payment = Payment.query.filter_by(transaction_id=reference).first()
        if not payment:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Security: Verify user owns this transaction
        if payment.buyer_id != session['user_id']:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'status': payment.status,
            'updated_at': payment.updated_at.isoformat() if payment.updated_at else None
        })
        
    except Exception as e:
        logging.error(f"Error in transaction status API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/paystack/webhook', methods=['POST'])
def paystack_webhook():
    """
    Handle Paystack webhook for payment verification
    Security: Verifies webhook signature, validates transaction
    """
    try:
        # Get the raw payload
        payload = request.get_data()
        
        # Security: Verify webhook signature
        signature = request.headers.get('X-Paystack-Signature')
        if not signature:
            logging.warning("Webhook received without signature")
            return jsonify({'error': 'No signature provided'}), 400
        
        # Compute expected signature
        secret_key = os.environ.get("PAYSTACK_SECRET_KEY")
        if not secret_key:
            logging.error("PAYSTACK_SECRET_KEY not found")
            return jsonify({'error': 'Configuration error'}), 500
            
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        # Security: Compare signatures using constant-time comparison
        if not hmac.compare_digest(signature, expected_signature):
            logging.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 403
        
        # Parse the event data
        try:
            event_data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            logging.error("Invalid JSON in webhook payload")
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Handle successful payment
        if event_data.get('event') == 'charge.success':
            transaction_data = event_data.get('data', {})
            reference = transaction_data.get('reference')
            status = transaction_data.get('status')
            
            if status == 'success' and reference:
                # Find the payment record
                payment = Payment.query.filter_by(transaction_id=reference).first()
                
                if payment and payment.status == 'pending':
                    # Update payment status
                    payment.status = 'completed'
                    
                    # Mark listing as unavailable
                    listing = Listing.query.get(payment.listing_id)
                    if listing:
                        listing.is_available = False
                    
                    db.session.commit()
                    
                    logging.info(f"Payment completed successfully: {reference}")
                    return jsonify({'status': 'success'}), 200
                else:
                    logging.warning(f"Payment record not found or already processed: {reference}")
                    return jsonify({'status': 'already_processed'}), 200
        
        # Handle failed payment
        elif event_data.get('event') == 'charge.failed':
            transaction_data = event_data.get('data', {})
            reference = transaction_data.get('reference')
            
            if reference:
                # Find and update payment record
                payment = Payment.query.filter_by(transaction_id=reference).first()
                if payment and payment.status == 'pending':
                    payment.status = 'failed'
                    db.session.commit()
                    
                    logging.info(f"Payment failed: {reference}")
        
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

