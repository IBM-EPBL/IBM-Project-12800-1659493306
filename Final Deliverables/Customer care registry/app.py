from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import sys
from markupsafe import escape
from flask_socketio import SocketIO, send, emit
import ElasticEmail
import uuid
from ElasticEmail.api import emails_api
from ElasticEmail.model.email_content import EmailContent
from ElasticEmail.model.body_part import BodyPart
from ElasticEmail.model.body_content_type import BodyContentType
from ElasticEmail.model.email_recipient import EmailRecipient
from ElasticEmail.model.email_message_data import EmailMessageData
from pprint import pprint






conn = ibm_db.connect("DATABASE=;HOSTNAME=;PORT=;SECURITY=;SSLServerCertificate=;UID = ;PWD=",'','')
print(conn)
print("connection successful...")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['DEBUG'] = True
socketio = SocketIO(app,cors_allowed_origins="*")
#===================================================
def fetch(sql):
    to_store=[]
    stmt = ibm_db.exec_immediate(conn, sql)
    data = ibm_db.fetch_both(stmt)

    while data != False:
            to_store.append(data)
            data = ibm_db.fetch_both(stmt) 
    return to_store

users = {}
@app.route('/chat<user>')
def chat(user):
    query=[]
    if user =='customer':
        sql = f"select * from complaint where RAISED_BY ='{escape(session['user_id'])}'"
        query=fetch(sql)                  
        for i in query:print(i)
        return render_template('ca_chatroom.html',name=session['name'],query=query)

    elif user == 'agent':
        sql = f"select * from complaint where ASSIGNED_AGENT ='{escape(session['user_id'])}' AND NOT CNAME = 'None' "
        query=fetch(sql)               
        for i in query:print(i)      
        print("agent"+str(query))

        return render_template('ca_chatroom_agent.html',name=session['name'],query=query)



@socketio.on('init')
def receive_username(userid):
    temp_user ={}
    private_serial_id=uuid.uuid4()
    temp_user['user_name']  = session['name']
    temp_user['user_id']    = session['user_id']
    temp_user['session_id'] = request.sid
    temp_user['is_Agent']   = session['is_agent']
    try:
        users[f"{private_serial_id}"]=temp_user
    except:
        private_serial_id=uuid.uuid4()
        users[f"{private_serial_id}"]=temp_user
    finally:
        print(str(users[f"{private_serial_id}"])+"added")
 

@socketio.on('private_message')
def private_message(payload):
    receivers=[]
    user_id = payload['userid']
    message=payload['message']
    print(user_id)
    if session['is_agent'] == True:

        
        for people in users.items():
            data=people[1]
            if (data['is_Agent'] == False) and (data['user_id'] == int(user_id)):
                emit('new_private_message', message, room=data['session_id'])
                receivers.append(people)
        print(receivers)
     

    else:
       for people in users.items():
            data=people[1]
            if (data['is_Agent'] == True) and (data['user_id'] == int(user_id)):
                emit('new_private_message', message, room=data['session_id'])
                receivers.append(people)
       print(receivers)

    
    print(payload['userid'])

    # emit('new_private_message', message, room=recipient_session_id)


#=========================================================================



@app.route('/')
def home():
    message = "TEAM ID : PNT2022TMID00312" +" "+ "BATCH ID : B2-2M4E "
    return render_template('home.html',mes=message)

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    return render_template('signin.html')

@app.route('/agentsignin', methods=['POST', 'GET'])
def agentsignin():

    return render_template('agent_signin.html')

@app.route('/signupage')
def signupage():

    return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print(request.form.get('login_as'))
    if  request.form.get('login_as')== 'customer':
     
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

        insert_sql = "INSERT INTO AGENTINFORMATION (EMAILID,AGENTPASSWORD,AGENTNAME,DATEOFBIRTH,AGENTID,ISAGENT) VALUES (?, ?, ?,?,a_id.nextval,'true')"
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
            sql = f"select * from NOTIFICATION where RECEIVER ='{escape(session['user_id'])}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            notifications_dict = ibm_db.fetch_both(stmt)

            unread=False

            while notifications_dict != False:
                unread=True                
                notifications.append(notifications_dict)
                notifications_dict = ibm_db.fetch_both(stmt)

            sql = f"select * from complaint where RAISED_BY ='{escape(session['user_id'])}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            query_dict = ibm_db.fetch_both(stmt)

            while query_dict != False:
                            
                query.append(query_dict)
                query_dict = ibm_db.fetch_both(stmt)
            print(query)

            if not unread:
                    return render_template("c_d.html",name=session['name'], notifications= notifications,query=query,otification_count='None so far')
            return render_template("c_d.html",name=session['name'], notifications= notifications,query=query,notification_count=len(notifications))

    

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

            if id=="000255@ccr.moc" and password =="255.0.0.0":
                return redirect(url_for('admin'))


            print(id, password)


            sql  = f"select * from user where  email='{escape(id)}' and passwordHash='{escape(password)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            data = ibm_db.fetch_both(stmt)
            # print("hello")

            
            session['name']=data['NAME']
        
            session['user_id']=data['USERID']
            session['is_agent']=False
            print(session['name'], session['user_id'],session['user_id'])
            #condition needs to be updated
           
            
            if data:

                session["email"] = escape(id)
                session["password"] = escape(password)
                flash("you are successfuly logged in")  
                return redirect(url_for('customer_dashboard',name=session['name']))
                
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
        ibm_db.bind_param(prep_stmt, 3, session['user_id'])
        ibm_db.bind_param(prep_stmt, 4,session['name'])
        ibm_db.execute(prep_stmt)
        print("query addeded")
        return redirect(url_for('customer_dashboard',name=session['name']))
    
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
        
    return render_template("admin_d.html",users=userdatabase)


@app.route('/complaints', methods=['POST', 'GET'])
def complaints():
    users    = request.args.get('users')
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
        
    return render_template("admin_d_query.html",query=complaints,agents=agents,users=users)

@app.route('/setcid', methods=['POST', 'GET'])
def setcid():
    print("hello im inside")
    c_id = request.args.get('layout')
    session["complaint_id"]=c_id
    print( c_id)
    return '', 204

@app.route('/setstatus', methods=['POST', 'GET'])
def setstatus():
    
    c_id = request.args.get('compl_id')
    update_stmt ="UPDATE complaint SET STATUS = ?  WHERE QUERYID = ?"

    prep_stmt = ibm_db.prepare(conn, update_stmt)
    ibm_db.bind_param(prep_stmt, 1,  escape('completed'))
    ibm_db.bind_param(prep_stmt, 2,  escape(c_id))

    ibm_db.execute(prep_stmt)

    print( "completed")
    return redirect(url_for('complaints'))

@app.route('/clarified', methods=['POST', 'GET'])
def clarified():
    
    c_id = request.args.get('q_id')
    update_stmt ="DELETE FROM complaint WHERE  QUERYID = ?"

    prep_stmt = ibm_db.prepare(conn, update_stmt)
    ibm_db.bind_param(prep_stmt, 1,  escape(c_id))

    ibm_db.execute(prep_stmt)

    print( "removed")
    return redirect(url_for('customer_dashboard'))

@app.route('/assign',methods=['POST', 'GET'])
def assign():
    users       = request.args.get('users')
    agent_id    = request.args.get('agent_id')
    agent_name  = request.args.get('agent_name')

    query_id    = session["complaint_id"]

    update_stmt ="UPDATE complaint SET ASSIGNED_AGENT = ?,ANAME= ?  WHERE QUERYID = ?"

    prep_stmt = ibm_db.prepare(conn, update_stmt)
    ibm_db.bind_param(prep_stmt, 1,  escape(agent_id))
    ibm_db.bind_param(prep_stmt, 2,  escape(agent_name))
    ibm_db.bind_param(prep_stmt, 3,  escape(session["complaint_id"]))
    ibm_db.execute(prep_stmt)

    #print(agent_id,agent_name,session["complaint_id"])


    sql = f"select * from complaint where  QUERYID ='{escape(query_id)}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    data = ibm_db.fetch_both(stmt)
    c_id=data['RAISED_BY']

    update_stmt ="UPDATE complaint SET STATUS = ?  WHERE QUERYID = ?"

    prep_stmt = ibm_db.prepare(conn, update_stmt)
    ibm_db.bind_param(prep_stmt, 1,  escape('agent assigned'))
    ibm_db.bind_param(prep_stmt, 2,  escape(query_id))

    ibm_db.execute(prep_stmt)

    sql  = f"SELECT * FROM user where  USERID ='{escape(c_id)}' "
    stmt = ibm_db.exec_immediate(conn, sql)
    c_data = ibm_db.fetch_both(stmt)
    c_email= c_data['EMAIL']
    c_name= c_data['NAME']
 
    configuration = ElasticEmail.Configuration()
    configuration.api_key['apikey'] = "0DA5443C60687801FD239BD2F9AF94C1CC2778A4B01D9B6F5842F925F54E49945C8F2049E46E041E520E4BFF7722C4E4"
    with ElasticEmail.ApiClient(configuration) as api_client:
        api_instance = emails_api.EmailsApi(api_client)
        email_message_data = EmailMessageData(
            recipients=[
                EmailRecipient(
                    email=c_email,
                    fields={
                        "name": c_name,
                        "agent":agent_name
                    },
                ),
            ],
            content=EmailContent(
                body=[
                    BodyPart(
                        content_type=BodyContentType("HTML"),
                        content="<h1>Hi {name}! <h1><br>{agent} has been assigned to you to clear your query<p></p>",
                        charset="utf-8",
                    ),
                    BodyPart(
                        content_type=BodyContentType("PlainText"),
                        content="Hi {name}! congratulations",
                        charset="utf-8",
                    ),
                ],
                _from="testccarereg@gmail.com",
                reply_to="testccarereg@gmail.com",
                subject="An Agent has been assigned to you",
            ),
        )
    try:
        api_response = api_instance.emails_post(email_message_data)
        pprint(api_response)
    except ElasticEmail.ApiException as e:
        print("Exception when calling EmailsApi->emails_post: %s\n" % e)

    insert_sql = "INSERT INTO NOTIFICATION  (THE_MESSAGE,RECEIVER,IS_AGENT) VALUES (?, ?, ?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)

    ibm_db.bind_param(prep_stmt, 1, escape(f"{agent_name} has been assigned to you on __time_stamp__"))
    ibm_db.bind_param(prep_stmt, 2, escape(c_id))
    ibm_db.bind_param(prep_stmt, 3, False)
    ibm_db.execute(prep_stmt)

 
    return redirect(url_for('complaints'))


@app.route('/agent_login', methods=['GET', 'POST'])
def agent_login():
   
    if request.method == 'POST':

        # try:
            id = request.form['email']
            password = request.form['password']
            if id=="000255@ccr.moc" and password =="255.0.0.0":
                return redirect(url_for('admin'))

            sql  = f"SELECT * FROM AGENTINFORMATION where  EMAILID ='{escape(id)}' and AGENTPASSWORD ='{escape(password)}'"
            stmt = ibm_db.exec_immediate(conn, sql)
            data = ibm_db.fetch_both(stmt)
           
            if data:

               
                session['name']=data['AGENTNAME']
                session['user_id']=data['AGENTID']
                session['is_agent']=True
                session["email"] = escape(id)
                session["password"] = escape(password)

                return redirect(url_for('agent_dashboard',agent_name=session['name']))
                
            else:
                print("mismatch")
        # except:
        #     print("except")
    else:
        print("error")
    return render_template("agent_signin.html")

@app.route('/agent_dashboard')
def agent_dashboard():

    query = []
    sql = f"select * from complaint where  ASSIGNED_AGENT ='{escape(session['user_id'])}'"
    stmt = ibm_db.exec_immediate(conn, sql)
    dict_1 = ibm_db.fetch_both(stmt)
    
    while dict_1 != False:
        query.append(dict_1)
        dict_1 = ibm_db.fetch_both(stmt)
        
    return render_template("agent_d.html",query=query)

@app.route('/complete')
def complete():

    
    agents = []
    sql = "SELECT * FROM AGENTINFORMATION"
    stmt = ibm_db.exec_immediate(conn, sql)
    dict_1 = ibm_db.fetch_both(stmt)
    
    while dict_1 != False:
        agents.append(dict_1)
        dict_1 = ibm_db.fetch_both(stmt)

    return render_template("admin_d_ agent.html",agents=agents)

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
    
        socketio.run(app,allow_unsafe_werkzeug=True, host='0.0.0.0')
        
