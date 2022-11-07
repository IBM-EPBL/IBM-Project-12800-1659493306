from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import sys
from markupsafe import escape
from flask_socketio import SocketIO, send, emit

print('app started')

global name

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=;PORT=;SECURITY=;SSLServerCertificate=;UID = ;PWD=",'','')
print(conn)
print("connection successful...")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['DEBUG'] = True


@app.route('/')
def home():
    message = "TEAM ID : PNT2022TMID00312" +" "+ "BATCH ID : B2-M24E "
    return render_template('signin.html',mes=message)



@app.route('/signin', methods=['POST', 'GET'])
def signin():
    return render_template('signin.html')


@app.route('/agentsignin', methods=['POST', 'GET'])
def agentsignin():

    return render_template('agent_signin.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/postquery')
def postquery():
    return render_template('c_dashboard_query.html')



@app.route('/agentregister', methods=['POST', 'GET'])
def agentregister():
    return render_template('agent_signin.html')



@app.route('/forgotpass', methods=['POST', 'GET'])
def forgotpass():
    return render_template('forgot.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
   
    if request.method == 'POST':

        try:
            print("try")

            id = request.form['email']
            password = request.form['password']


            print(id, password)


            sql = f"select * from user where  email='{escape(id)}' and passwordHash='{escape(password)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            data = ibm_db.fetch_both(stmt)
            print("hello")
            
            if data:
                session["email"] = escape(id)
                session["password"] = escape(password)
              
                name=data['NAME']
                return render_template("customer_dashboard.html",name=name)

            else:
                print("mismatch")
        except:
            print("except")
    else:
        print("error")
    return render_template("signin.html")

    
@app.route('/admin', methods=['POST', 'GET'])
def admin():
    userdatabase = []
    sql = "SELECT * FROM user"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    
    while dictionary != False:
        userdatabase.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    print(userdatabase)
        
    return render_template("admin_dashboard.html",users=userdatabase)

if __name__ == '__main__':
        app.run()