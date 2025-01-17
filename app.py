from flask import Flask, request, redirect, url_for, render_template, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import pdfkit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dr-notepad-online' 

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', documents=documents)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            return jsonify(error=str(e)), 500
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/add_document', methods=['POST'])
@login_required
def add_document():
    data = request.json
    title = data['title']
    content = data['content']
    document = Document.query.filter_by(title=title, user_id=current_user.id).first()
    if document:
        document.content = content
    else:
        document = Document(title=title, content=content, user_id=current_user.id)
        db.session.add(document)
    db.session.commit()
    return jsonify(success=True, message='Document saved successfully.')

@app.route('/get_document')
@login_required
def get_document():
    title = request.args.get('title')
    document = Document.query.filter_by(title=title, user_id=current_user.id).first()
    if document:
        return jsonify(success=True, content=document.content)
    else:
        return jsonify(success=False, message="Document not found"), 404

@app.route('/save_pdf', methods=['POST'])
@login_required
def save_pdf():
    data = request.get_json()
    title = data['title'].replace(" ", "_")
    content = data['content']
    document = Document.query.filter_by(title=title, user_id=current_user.id).first()
    if document:
        document.content = content
    else:
        document = Document(title=title, content=content, user_id=current_user.id)
        db.session.add(document)
    db.session.commit()

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8"
    }
    try:
        pdf = pdfkit.from_string(content, False, options=options, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{title}.pdf"'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
