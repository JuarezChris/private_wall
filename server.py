from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL    # import the function that will return an instance of a connection
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "keep it secret" 
# ******************** root route ************************
@app.route("/")
def index():
    mysql = connectToMySQL('private_wall')	        # call the function, passing in the name of our db
    users = mysql.query_db('SELECT * FROM userdb;')  # call the query_db function, pass in the query as a string
    # print(users)
    return render_template("index.html")

# ******************** create user ************************
@app.route("/create_user", methods=["POST"])
def add_user_to_db():
    is_valid = True
    if len(request.form['fname']) < 1:
        is_valid = False
        flash("Please enter a first name")
    if len(request.form['lname']) < 1:
        is_valid = False
        flash("Please enter last name")
    if not EMAIL_REGEX.match(request.form['email']):    # test whether a field matches the pattern
        is_valid = False
        flash("Invalid email address!")  
    if len(request.form['password']) < 8:
        is_valid = False
        flash("password should be at least 8 characters")
    if str(request.form["cpassword"]) != str(request.form["password"]):
        is_valid = False
        flash("password does not match")

    if not is_valid:
        return redirect("/")
    else:
    	# add user to database
        query= "INSERT INTO userdb (first_name, last_name, email, password, confirm_password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pass)s, %(conpass)s, NOW(), NOW());"
        data = {
        "fn": request.form["fname"],
        "ln": request.form["lname"],
        "em": request.form["email"],
        "pass": request.form["password"],
        "conpass": request.form["cpassword"]
        }
        session['email']= request.form['email']
        session['userfname']= request.form['fname']
        query1 = "SELECT * FROM userdb WHERE email = %(email)s;"
        data1 = { 
            'email' : session['email']
        }
        db = connectToMySQL('private_wall')
        result = db.query_db(query, data)
        mysql = connectToMySQL('private_wall')
        users = mysql.query_db('SELECT * FROM userdb;')
        # print(users)
        for x in users:
            # print(x['email'])
            if x['email'] == session['email']:
                session['id']= x['id']
                break;
        
        flash("User successfully added!")
    return redirect("/wall")

# *******************success page*************************
@app.route("/wall")
def success():
    if 'email' in session:
        mysql = connectToMySQL('private_wall')
        users = mysql.query_db('SELECT * FROM userdb;')
        db = connectToMySQL('private_wall')
        messages = db.query_db('SELECT * FROM messagesdb;')
        return render_template("wall.html", all_users = users, all_messages = messages)
    else:
        return redirect("/")

# ******************** user login ************************
@app.route("/user_login", methods=["POST"])
def check_user_in_db():
    db = connectToMySQL('private_wall')
    is_valid = True
    if not EMAIL_REGEX.match(request.form['email']):    # test whether a field matches the pattern
        is_valid = False
        flash("Invalid email address!")
    if len(request.form['password']) < 2:
        is_valid = False
        flash("password should be at least 2 characters")
    
    
    if not is_valid:
        return redirect("/")
    else:
    	# login
        query = "SELECT * FROM userdb WHERE email = %(email)s;"
        data = { 
            'email' : request.form['email']
        }
        
        session['email']= request.form['email']
        result = db.query_db(query, data)
        print(result)
        session['id']= result[0]['id']
        # session['user_first_name'] = result[0]['first_name']
        session['userfname']= result[0]['first_name']

    return redirect("/wall")

# ******************* logout *************************
@app.route("/exit")
def logout():
    # Remove session data, this will log the user out
   session.pop('email', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect('/')

# ******************* create message *************************
@app.route("/send_message/<int:one_user>", methods=["POST"])
def create_mess(one_user):
    print(one_user)
    is_valid = True
    if len(request.form['message']) < 5:
        is_valid = False
        flash("message should be at least 5 characters")
    
    
    if not is_valid:
        return redirect("/wall")
    else:
        reciever = one_user
    #    reciever = message.query.get(reciever_id)
        query= "INSERT INTO messagesdb (sent_id, recieved_id, messages, created_at, updated_at) VALUES (%(sent)s, %(rec)s, %(mess)s, NOW(), NOW());"
        data = {
        'sent': session['id'],
        'rec': reciever,
        'mess': request.form['message']
        
        }
        db = connectToMySQL('private_wall')
        result = db.query_db(query, data)
    return redirect('/wall')


# ******************* delete message *************************
@app.route("/delete/<int:one_mess>")
def destroy(one_mess):
    print(one_mess)
    query= "DELETE FROM messagesdb WHERE message_id = %(id_num)s;"
    data = {
        'id_num': one_mess
        }
    db = connectToMySQL('private_wall')
    result = db.query_db(query, data)
    return redirect("/wall")

if __name__ == "__main__":
    app.run(debug=True)