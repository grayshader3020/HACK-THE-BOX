from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymatgen.io.cif import CifParser
import hashlib
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MyS3cretCh3mistry4PP'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'cif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Structure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(150), nullable=False)
    identifier = db.Column(db.String(100), nullable=False, unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_density(structure):
    atomic_mass_Si = 28.0855
    num_atoms = 2
    mass_unit_cell = num_atoms * atomic_mass_Si
    mass_in_grams = mass_unit_cell * 1.66053906660e-24
    volume_in_cm3 = structure.lattice.volume * 1e-24
    density = mass_in_grams / volume_in_cm3
    return density

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == hashlib.md5(password.encode()).hexdigest():
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    structures = Structure.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', structures=structures)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        identifier = str(uuid.uuid4())
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], identifier + '_' + filename)
        file.save(filepath)
        new_structure = Structure(user_id=current_user.id, filename=filename, identifier=identifier)
        db.session.add(new_structure)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return redirect(request.url)

@app.route('/structure/<identifier>')
@login_required
def show_structure(identifier):
    structure_entry = Structure.query.filter_by(identifier=identifier, user_id=current_user.id).first_or_404()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], structure_entry.identifier + '_' + structure_entry.filename)
    parser = CifParser(filepath)
    structures = parser.parse_structures()
    
    structure_data = []
    for structure in structures:
        sites = [{
            'label': site.species_string,
            'x': site.frac_coords[0],
            'y': site.frac_coords[1],
            'z': site.frac_coords[2]
        } for site in structure.sites]
        
        lattice = structure.lattice
        lattice_data = {
            'a': lattice.a,
            'b': lattice.b,
            'c': lattice.c,
            'alpha': lattice.alpha,
            'beta': lattice.beta,
            'gamma': lattice.gamma,
            'volume': lattice.volume
        }
        
        density = calculate_density(structure)
        
        structure_data.append({
            'formula': structure.formula,
            'lattice': lattice_data,
            'density': density,
            'sites': sites
        })
    
    return render_template('structure.html', structures=structure_data)

@app.route('/delete_structure/<identifier>', methods=['POST'])
@login_required
def delete_structure(identifier):
    structure = Structure.query.filter_by(identifier=identifier, user_id=current_user.id).first_or_404()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], structure.identifier + '_' + structure.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(structure)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)