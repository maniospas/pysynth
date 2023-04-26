from traceback import format_exc
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required
import pysynth


app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    additions = db.relationship('Entry', backref=db.backref('user', uselist=False), lazy=True)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def owner(self):
        return User.query.get_or_404(self.creator_id).username

    def permissions(self):
        return self.creator_id == current_user.id or current_user.is_admin


with app.app_context():
    db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        remember = True if request.form.get('remember') else False
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='sha256')
        user = User(username=username, password=hashed_password)

        if Entry.query.count() == 0:
            user.is_admin = True

        try:
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=remember)
            #flash('Registration successful. Please log in.')
            return redirect(url_for('index'))
        except:
            flash('Account already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST' and request.form['q']:
        query = request.form['q']
        keywords = [word.strip() for word in pysynth.specs(query) if word.strip()]
        try:
            database = pysynth.Database()
            found = set()
            for word in keywords:
                for entry in Entry.query.filter(Entry.name.contains(word)):
                    if entry.id not in found:
                        database.add(pysynth.tomodel(entry.code))
                        found.add(entry.id)
            implementation = pysynth.Multispecs(pysynth.Synthesizer(database))(query)
            remainder = ", ".join(implementation.specifications)
            if remainder:
                flash("Not covered: "+remainder, 'warning')
            implementation.order()
            implementation = '\n'.join(list(set(str(expr) for expr in implementation.dependencies))+ [str(expr) for expr in implementation.expressions])
        except Exception as e:
            flash(str(e), 'danger')
            implementation = format_exc() if current_user.is_admin else ""
            return render_template('index.html', query=query, implementation=implementation)
    else:
        query = ""
        implementation = ""
    return render_template('index.html', query=query, implementation=implementation)


@app.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    if request.method == 'POST' and request.form['q']:
        query = request.form['q']
        entries = Entry.query.filter(Entry.name.contains(query))
    else:
        query = ""
        entries = Entry.query.all()
    return render_template('data.html', entries=entries, query=query)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form['name']
        source = request.form['source']
        code = request.form['code']
        entry = Entry(name=name, source=source, code=code, creator_id=current_user.id)
        db.session.add(entry)
        db.session.commit()
        flash('Model added successfully', 'info')
        return redirect(url_for('data'))
    return render_template('add.html')


@app.route('/permissions/<int:user_id>', methods=['POST'])
@login_required
def permissions(user_id: int):
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        user = User.query.get_or_404(user_id)
        user.is_admin = True
        db.session.commit()
        flash(f'Added administrator permissions to {user.username}', 'info')
        return redirect(url_for('users'))
    return render_template('admin.html', users=User.query.all())


@app.route('/users', methods=['GET'])
@login_required
def users():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin.html', users=User.query.all())


@app.route('/parse', methods=['GET', 'POST'])
@login_required
def parse():
    if request.method == 'POST':
        source = request.form['source']
        code = request.form['code']
        added = 0
        for code in pysynth.blocks(code):
            model = pysynth.tomodel(code, source)
            name = ", ".join(set([spec.strip() for spec in model.specifications if spec.strip()]))
            entry = Entry(name=name, source=source, code=code, creator_id=current_user.id)
            db.session.add(entry)
            added += 1
        db.session.commit()
        flash(f'Added {added} models', 'info')
        return redirect(url_for('data'))
    return render_template('parse.html')


@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if not entry.permissions():
        abort(403)  # Forbidden
    if request.method == 'POST':
        entry.name = request.form['name']
        entry.source = request.form['source']
        entry.code = request.form['code']
        db.session.commit()
        flash('Entry updated successfully')
        return redirect(url_for('data'))
    return render_template('edit.html', entry=entry)


@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    if not entry.permissions():
        abort(403)  # Forbidden
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted successfully')
    return redirect(url_for('data'))


