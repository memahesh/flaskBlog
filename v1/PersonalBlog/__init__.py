import os

from flask import Flask

# Database Connection
from . import db

# Importing Blueprints
from . import auth
from . import blog

def create_app(test_config=None):
	
	app = Flask(__name__, instance_relative_config = True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'data.sqlite')
	)

	if test_config is None:
		# When not testing, load the Instance config (original) if it exists
		app.config.from_pyfile('config.py', silent=True)
	else:
		app.config.from_mapping(test_config)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Database Connections
	db.init_app(app)	

	# Registering Blueprints
	app.register_blueprint(auth.bp)
	app.register_blueprint(blog.bp)
	# Now both url_for('blog.index') as well as url_for('index') both work and point to url (domainname/)
	app.add_url_rule('/', endpoint='index')

	@app.route('/hello')
	def hello():
		return "I need to get my daily dose of sunshine"

	return app

