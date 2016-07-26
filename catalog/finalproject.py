#Main application code
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

####### LOGIN #######
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

####### GCONNECT #######
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    print "done!"
    return output

	

####### GDISCONNECT #######	
@app.route('/gdisconnect')
def gdisconnect():
	# Only disconnect a connected user.     
	c = login_session['access_token']
	print 'In gdisconnect access token is %s', c
	print 'user name is' 
	print login_session['username']
	if c is None:
		print 'Credentials is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200': 
		del login_session['access_token'] 
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response

		
####### USER ID ########
def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None
	
####### USER INFO ########
def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user
	
####### CREATE USER ########
def createUser(login_session):
	newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id
	

		
####### VIEW CATEGORIES (MAIN PAGE)######
@app.route('/')
@app.route('/Category/')
def showCategory():
	categories = session.query(Category).order_by(Category.name)
	
	if 'username' not in login_session:
		return render_template('publiccategory.html', categories=categories)
	else:
		return render_template('category.html', categories=categories)
	


####### VIEW ITEMS BY CATEGORY ##########	
@app.route('/Category/<int:category_id>/')
def showCategoryItems(category_id):
	category = session.query(Category).filter_by(id = category_id).one()
	creator = getUserInfo(category.user_id)
		
	items = session.query(Item).filter_by(category_id=category_id).all()
	
	
	if 'username' not in login_session or creator.id != login_session['user_id']:
		return render_template('publicitem.html', category=category, items=items)
	else:
		return render_template('item.html', category=category, items=items)

	
###### ADD CATEGORY ########	
@app.route('/Category/new/', methods=['GET','POST'])
def newCategory():
	if 'username' not in login_session:
		return redirect('/login')
		
	if request.method == 'POST':
		newCategory = Category(name = request.form['name'], user_id=login_session['user_id'])
		session.add(newCategory)
		session.commit()
		flash('New category created!')
		return redirect(url_for('showCategory'))
	else:
		return render_template('newcategory.html')

####### EDIT CATEGORY ########
@app.route('/Category/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
	if 'username' not in login_session:
		return redirect('/login')
		
	editedCategory = session.query(Category).filter_by(id = category_id).one()
	
	if editedCategory.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this category. Please create your own category in order to edit.');}</script><body onload='myFunction()''>"

	if request.method == 'POST':
		if request.form['name']:
			editedCategory.name=request.form['name']
		session.add(editedCategory)
		session.commit()
		flash('Category edited!')
		return redirect(url_for('showCategoryItems', category_id=editedCategory.id))
	else:
		return render_template('editcategory.html', category=editedCategory)

######## DELETE CATEGORY#########
@app.route('/Category/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCategory(category_id):
	if 'username' not in login_session:
		return redirect('/login')
	
	deletedCategory = session.query(Category).filter_by(id = category_id).one()
	
	if deletedCategory.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this category. Please create your own category in order to edit.');}</script><body onload='myFunction()''>"
	
	if request.method == 'POST':
		session.delete(deletedCategory)
		session.commit()
		flash('Category deleted!')
		return redirect(url_for('showCategory'))
	else:
		return render_template('deletecategory.html', category=deletedCategory)

		
######## ADD ITEM ############
@app.route('/Category/<int:category_id>/new/', methods=['GET','POST'])
def newItem(category_id):
	if 'username' not in login_session:
		return redirect('/login')
		
	category=session.query(Category).filter_by(id = category_id).one()
	
	if category.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to add items to this category. Please create your own category in order to add items.');}</script><body onload='myFunction()''>"
	
	if request.method == 'POST':
		newItem = Item(name = request.form['name'],description = request.form['description'],price = request.form['price'],color = request.form['color'], category_id = category_id, user_id=login_session['user_id'])
		session.add(newItem)
		session.commit()
		flash('New item created!')
		return redirect(url_for('showCategoryItems', category_id=category_id))
	else:
		return render_template('newitem.html', category=category)
	

######## EDIT ITEM ############
@app.route('/Category/<int:category_id>/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(category_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
		
	editedItem = session.query(Item).filter_by(id=item_id).one()
	
	if editedItem.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to edit.');}</script><body onload='myFunction()''>"
	
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name=request.form['name']
		if request.form['description']:
			editedItem.description=request.form['description']
		if request.form['color']:
			editedItem.color=request.form['color']
		if request.form['price']:
			editedItem.price=request.form['price']
		session.add(editedItem)
		session.commit()
		flash('Item edited!')
		return redirect(url_for('showCategoryItems', category_id=category_id))
	else:
		return render_template('edititem.html', category_id=category_id, item=editedItem)
		
######## DELETE ITEM ############
@app.route('/Category/<int:category_id>/<int:item_id>/delete/', methods=['GET','POST'])
def deleteItem(category_id, item_id):
	if 'username' not in login_session:
		return redirect('/login')
		
	deletedItem = session.query(Item).filter_by(id=item_id).one()
	
	if deletedItem.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to edit.');}</script><body onload='myFunction()''>"
	
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash('Item deleted!')
		return redirect(url_for('showCategoryItems', category_id=category_id))
	else:
		return render_template('deleteitem.html', category_id=category_id, item=deletedItem)

		
		
######## CATEGORIES JSON ##########
@app.route('/Category/JSON/')
def categoryJSON():
	categories = session.query(Category).all()
	return jsonify(Categories=[c.serialize for c in categories])
		
######## CATEGORY ITEMS JSON ##########
@app.route('/Category/<int:category_id>/JSON/')
def categoryItemJSON(category_id):
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(Item).filter_by(category_id=category_id).all()
	return jsonify(CategoryItems=[i.serialize for i in items])
	
######## ITEM JSON ##########
@app.route('/Category/<int:category_id>/<int:item_id>/JSON/')
def itemJSON(category_id, item_id):
	item = session.query(Item).filter_by(id=item_id).one()
	return jsonify(Item = item.serialize)
	


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug=True
	app.run(host = '0.0.0.0', port = 5000)
	
	
	
