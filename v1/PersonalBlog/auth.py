import functools

from flask import Blueprint, g, url_for, render_template, redirect, request, session, flash

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		
		if 'user_id' in session:
			return "Please <a href='/auth/logout'>logout</a> before trying to register"
	
		username = request.form['username']
		password = request.form['password']
		db = get_db()
        	
		if username and password:
			
			if db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
				flash("User with username {} is already registered".format(username))
			else:
				db.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, generate_password_hash(password)))
				db.commit()
				session.clear()
				return redirect(url_for('auth.login'))

		else:
			flash("Need both username and password")
	
	return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
	
		if 'user_id' in session:
			return "Please <a href='/auth/logout'>logout</a> before trying to login again"
	
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		user = db.execute(
			'SELECT * FROM user WHERE username = ?', (username,)
		).fetchone()

		if user is None:
			flash("No user exists with username {}".format(username))
		elif not check_password_hash(user['password'], password):
			flash("Please check your password.")
		else:
			session.clear()
			session['user_id'] = user['id']
			return redirect(url_for('index'))

	return render_template('auth/login.html')	


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
