try:
    from flask import Flask, render_template, request, redirect, jsonify
    from flask_sqlalchemy import SQLAlchemy
except (ImportError, ModuleNotFoundError):  # pragma: no cover - allow editors/linters without Flask installed
    # Provide fallbacks to avoid import errors in environments where Flask
    # is not available (e.g., some editors or static analysis tools).
    Flask = None
    render_template = None
    request = None
    redirect = None
    jsonify = None
    SQLAlchemy = None

try:
    from flask_mail import Mail, Message
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    Mail = None
    Message = None

if Flask is None:
    raise ImportError("Flask is required but not installed. Install it with: pip install flask flask-sqlalchemy flask-mail")

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration (Optional Bonus)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'

db = SQLAlchemy(app)
mail = Mail(app) if Mail else None

# Database Model
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    business_type = db.Column(db.String(100))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='New')

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Submit Lead
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    business_type = request.form['business_type']
    message = request.form['message']

    new_lead = Lead(
        name=name,
        email=email,
        phone=phone,
        business_type=business_type,
        message=message
    )

    db.session.add(new_lead)
    db.session.commit()

    # Auto Reply Email
    try:
        msg = Message(
            'Thank You',
            sender='your_app_password',
            recipients=[email]
        )

        msg.body = f"""
Hi {name},

Thank you for contacting us.
We received your message successfully.

We will contact you soon.

Regards,
Lead Management Team
"""

        mail.send(msg)

    except Exception as e:
        print("Email Error:", e)

    return redirect('/')

# Dashboard
@app.route('/dashboard')
def dashboard():
    search = request.args.get('search', '')

    if search:
        leads = Lead.query.filter(
            Lead.name.contains(search) |
            Lead.email.contains(search)
        ).all()
    else:
        leads = Lead.query.all()

    return render_template('dashboard.html', leads=leads)

# Update Status
@app.route('/update/<int:id>/<status>')
def update_status(id, status):
    lead = Lead.query.get(id)

    if lead:
        lead.status = status
        db.session.commit()

    return redirect('/dashboard')

# Run Application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)