from flask import Flask, request, render_template
from flask import make_response
import pymysql
from flask.ext.mysql import MySQL
from flask_bcrypt import Bcrypt
import time

#setting up flask
app = Flask(__name__)
#setting up MySQL
mysql = MySQL()
#setting up the database credentials and getting the MySQL library to work with the flask libray
app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_USER'] = "birduser"
app.config['MYSQL_DATABASE_PASSWORD'] = "Draco<3Orion"
#the schema name
app.config['MYSQL_DATABASE_DB'] = "bird_camera"
mysql.init_app(app)

#the number of nests you'd like to display
NUMBER_OF_ACTIVE_NESTS=6

#The html template for information about each nest
#{0} is for the nest's number, and {1} is for the list of bird names
nestHTML = '''<li>
			  <h2>Nest {0}
			    <!-- clicking on the cross will show the form for adding a new bird -->
			  	<img class="add" src="/static/images/cross.svg" style="padding-left:10px;" width=20px onclick="showForm('nest{0}')"/>
			  </h2>
			  Home to:
			  <ol>
			  {1}
			  </ol>
			  <!-- this form is hidden until the cross is clicked -->
			  <form method="POST" id="nest{0}" class="nest">
				birdName </br>
				<input type="text" name="nm" required />
				<input type="submit" value="save" />
				<input style="display:none;" type="number" value="{0}" name="nest" />
			  </form>
			  </li>
			'''

def get_birds_from_nest(number):
	'''retrieves all the bird's names and their age from the nest specified'''
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute("SELECT birdName, timeDiscovered FROM birds WHERE nestID={0};".format(number))
	return cursor.fetchall()

def add_bird(name, nest):
	'''adds a new bird to the database'''
	conn = mysql.connect()
	cursor = conn.cursor()
	#sets the bird's birth date to the current time
	current_time = time.time()
	cursor.execute("INSERT INTO birds (birdName, timeDiscovered, nestID) VALUES (\'{0}\', \'{1}\', {2});".format(name, current_time, nest))
	conn.commit()

@app.route('/', methods=['POST', 'GET'])
def index():
	#if the form has been submitted then get the values of the inputs from the form
	# and call the add bird function
	if request.method == "POST":
		name = request.form['nm']
		nestID = request.form['nest']
		add_bird(name, nestID)
	total_nests = ''
	#build up the information for the page using the nest templates
	for nest in range(NUMBER_OF_ACTIVE_NESTS):
		#build up the information about the birds belonging to each nest
		#{0} is for the bird name, {1} is for the number of weeks, {2} for the
		#number of days and {3} is to leave space for another <li> element to be added
		list_item = '<li> {0} who</br> is {1} week/s + </br> {2} day/s old </li> {3}'
		list_of_birds = ''
		current_time = time.time()
		for bird in get_birds_from_nest(nest + 1):
			age = current_time - float(bird[1])
			age_weeks = str(int(age // (60*60*24*7))) #convert the seconds to weeks
			age_days_left_over = str(int(age % (60*60*24*7) // (60*60*24))) #convert the remainding seconds to days
			list_of_birds += list_item.format(bird[0], age_weeks, age_days_left_over,'{0}') #place info into the li template, {0} leaves a gap for the next li
		list_of_birds = list_of_birds.format('') #removes the final {0} as no more li need to be added
		total_nests += nestHTML.format(nest + 1, list_of_birds) #adds the nests to the main page
	#updates the page being displayed
	return render_template("index.html", nests=total_nests)
