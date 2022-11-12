from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import sys
from markupsafe import escape
from flask_socketio import SocketIO, send, emit
global name
global customer_id

# conn = ibm_db.connect()
# print(conn)
# print("connection successful...")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['DEBUG'] = True
socketio = SocketIO(app,cors_allowed_origins="*")

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("imin")
    if  request.args.get('login_as')== 'customer':
        print("imin1")
        insert_sql = "INSERT INTO user (email,passwordHash,name,dob) VALUES (?, ?, ?,?)"
        
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, escape(request.form['email']))
        ibm_db.bind_param(prep_stmt, 2, escape(request.form['password']))
        ibm_db.bind_param(prep_stmt, 3,  escape(request.form['firstname']+ escape(request.form['lastname'])))
        ibm_db.bind_param(prep_stmt, 4,  escape(request.form['DOB'][::-1]))
        ibm_db.execute(prep_stmt)

        print("user addeded")
        return redirect(url_for('signin'))

    else:

        insert_sql = "INSERT INTO AGENTINFORMATION (EMAILID,AGENTPASSWORD,AGENTNAME,DATEOFBIRTH,AGENTID) VALUES (?, ?, ?,?,a_id.nextval)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, escape(request.form['email']))
        ibm_db.bind_param(prep_stmt, 2, escape(request.form['password']))
        ibm_db.bind_param(prep_stmt, 3,  escape(request.form['firstname']+ escape(request.form['lastname'])))
        ibm_db.bind_param(prep_stmt, 4,  escape(request.form['DOB']))
    
        ibm_db.execute(prep_stmt)

        print("agent addeded")
        return redirect(url_for('agentsignin'))

@app.route('/customer_dashboard')
def customer_dashboard():
            notifications=[]
            query=[]
            sql = f"select * from NOTIFICATION where RECEIVER ='{escape(customer_id)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            notifications_dict = ibm_db.fetch_both(stmt)

            unread=False

            while notifications_dict != False:
                unread=True                
                notifications.append(notifications_dict)
                notifications_dict = ibm_db.fetch_both(stmt)

            sql = f"select * from complaint where RAISED_BY ='{escape(customer_id)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            data = ibm_db.fetch_both(stmt)
            query_dict = ibm_db.fetch_both(stmt)

            while query_dict != False:
                            
                query.append(query_dict)
                query_dict = ibm_db.fetch_both(stmt)

            if not unread:
                    return render_template("c_d.html",name=name, notifications= notifications,query=query,otification_count='None so far')
            return render_template("c_d.html",name=name, notifications= notifications,query=query,notification_count=len(notifications))

    

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
            id = request.form['email']
            password = request.form['password']
            sql  = f"select * from user where  email='{escape(id)}' and passwordHash='{escape(password)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            data = ibm_db.fetch_both(stmt)
            # print("hello")

            global name
            name=data['NAME']
            global customer_id
            customer_id=data['USERID']
            
            if data:

                session["email"] = escape(id)
                session["password"] = escape(password)
                return redirect(url_for('customer_dashboard',name=name))
                
            else:
                print("mismatch")
        except:
            print("except")
    else:
        print("error")
    return render_template("signin.html")

@app.route('/postnow', methods=['POST', 'GET'])
def post():

        insert_sql = "INSERT INTO complaint (description,status,raised_by,CNAME) VALUES (?, ?, ?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, escape(request.form['query']))
        ibm_db.bind_param(prep_stmt, 2,'not complete')
        ibm_db.bind_param(prep_stmt, 3, customer_id)
        ibm_db.bind_param(prep_stmt, 4, name)
        ibm_db.execute(prep_stmt)
        print("query addeded")
        return redirect(url_for('customer_dashboard',name=name))
    
@app.route('/admin', methods=['POST', 'GET'])
def admin():
    userdatabase = []
    sql = "SELECT * FROM user"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    
    while dictionary != False:
        userdatabase.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
   
    return render_template("admin_d.html",users=userdatabase)


@app.route('/complaints', methods=['POST', 'GET'])
def complaints():
    complaints = []
    sql = "SELECT * FROM complaint"
    stmt = ibm_db.exec_immediate(conn, sql)
    dict_0 = ibm_db.fetch_both(stmt)
    
    while dict_0 != False:
        complaints.append(dict_0)
        dict_0 = ibm_db.fetch_both(stmt)
    
    agents = []
    sql = "SELECT * FROM AGENTINFORMATION"
    stmt = ibm_db.exec_immediate(conn, sql)
    dict_1 = ibm_db.fetch_both(stmt)
    
    while dict_1 != False:
        agents.append(dict_1)
        dict_1 = ibm_db.fetch_both(stmt)

    print(complaints)
        
    return render_template("admin_d_query.html",query=complaints,agents=agents)

@app.route('/setcid', methods=['POST', 'GET'])
def setcid():
    print("hello im inside")
    c_id = request.args.get('layout')
    session["complaint_id"]=c_id
    print( c_id)
    return '', 204

@app.route('/assign',methods=['POST', 'GET'])
def assign():
    agent_id    = request.args.get('agent_id')
    agent_name  = request.args.get('agent_name')
    query_id    = session["complaint_id"]

    update_stmt ="UPDATE complaint SET ASSIGNED_AGENT = ?,ANAME= ?  WHERE QUERYID = ?"

    prep_stmt = ibm_db.prepare(conn, update_stmt)
    ibm_db.bind_param(prep_stmt, 1,  escape(agent_id))
    ibm_db.bind_param(prep_stmt, 2,  escape(agent_name))
    ibm_db.bind_param(prep_stmt, 3,  escape(session["complaint_id"]))
    ibm_db.execute(prep_stmt)
    return redirect(url_for('complaints'))


@app.route('/agent_login', methods=['GET', 'POST'])
def agent_login():
   
    if request.method == 'POST':

        # try:
            id = request.form['email']
            password = request.form['password']

            sql  = f"SELECT * FROM AGENTINFORMATION where  EMAILID ='{escape(id)}' and AGENTPASSWORD ='{escape(password)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            data = ibm_db.fetch_both(stmt)
           
            if data:

                global agent_name
                agent_name=data['AGENTNAME']
                global agent_id
                agent_id=data['AGENTID']

                session["a_email"] = escape(id)
                session["a_password"] = escape(password)

                return redirect(url_for('agent_dashboard',agent_name=agent_name))
                
            else:
                print("mismatch")
        # except:
        #     print("except")
    else:
        print("error")
    return render_template("agent_signin.html")
@app.route('/admin_agent')
def admin_agent():

    
    agents = []
    sql = "SELECT * FROM AGENTINFORMATION"
    stmt = ibm_db.exec_immediate(conn, sql)
    dict_1 = ibm_db.fetch_both(stmt)
    
    while dict_1 != False:
        agents.append(dict_1)
        dict_1 = ibm_db.fetch_both(stmt)

    return render_template("admin_d_ agent.html",agents=agents)
if __name__ == '__main__':
        socketio.run(app)
