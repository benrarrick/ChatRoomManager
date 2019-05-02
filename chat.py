#Benjamin Rarrick
#btr21 3929011
#Project 2
#7/1/18
 
from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy import func
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
app.secret_key = "yet another deplorable secret key"

#########################################   Model #################################################

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r %r>' % (self.id, self.username)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "password": self.password,
        }


class Chatroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ownerID = db.Column(db.String(30), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, ownerID, name):
        self.ownerID = ownerID
        self.name = name

    def __repr__(self):
        return '<ChatRoom %r %r>' % (self.ownerID, self.name)

    def as_dict(self):
        return {
            "id": self.id,
            "ownerID": self.ownerID,
            "name": self.name
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomID = db.Column(db.Integer, db.ForeignKey('chatroom.id'), nullable=False)
    senderID = db.Column(db.Integer, db.ForeignKey('user.id'))
    senderName = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(140), nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __init__(self, roomID, senderID, senderName, message, time):
        self.roomID = roomID
        self.senderID = senderID
        self.senderName = senderName
        self.message = message
        self.time = time

    def __repr__(self):
        return '<Message = %r %r %r %r %r %r >' % (self.id, self.roomID, self.senderID,
                                                   self.senderName, self.message, self.time)

    def as_dict(self):
        return {
            "id": self.id,
            "roomID": self.roomID,
            "senderID": self.senderID,
            "senderName": self.senderName,
            "message": self.message,
            "time": self.time
        }

@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()
    print('The Database has been initialized')
    
    
#########################################   Routes #################################################
@app.route("/")
def logOrSign():
    if 'user' in session:
        return redirect(url_for('main'))
    else:
        return render_template("login.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    print("in login")
    if request.method == "GET":
        return redirect(url_for("logOrSign"))
    else:
        print("in else")
        usr = request.form['lusername']
        psw = request.form['lpassword']

        if len(usr) == 0 or len(psw) == 0:
            flash("Please enter information into all fields.")
            return redirect(url_for('logOrSign'))
        else:
            user = User.query.filter(and_(User.username == usr, User.password == psw)).first()
            if user:
                session['user'] = user.as_dict()
                session['user']['activeRoom'] = -1
                session.modified = True
                return redirect(url_for('main'))
            else:
                flash('Username or password incorrect.')
                return redirect(url_for('logOrSign'))
                
@app.route('/logout',  methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("logOrSign"))

#route to create an account
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return redirect(url_for("logOrSign"))
    else:
        name = request.form['sname']
        usr = request.form['susername']
        psw = request.form['spassword']
        if len(name)==0 or len(usr) == 0 or len(psw) == 0:
            flash("Please enter information into all fields.")
            return redirect(url_for("logOrSign"))
        newUser = User.query.filter_by(username=usr).first()
        if newUser == None:
            user = User(name, usr, psw)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.as_dict()
            session['user']['activeRoom'] = -1
            session.modified = True
            return redirect(url_for("main"))
        else:
            flash('That username has already been taken')
            return redirect(url_for("logOrSign"))

#main page that lists the user's rooms and other rooms
@app.route("/main")
def main():
    if 'user' in session:
        session['main'] = populateSession(session['user'])
        return render_template("main.html", user=session['main'])
    else:
        return redirect(url_for("logOrSign"))
        
#render chatroom page and populate the session witht the room information    
@app.route('/room/<int:roomID>')
def room(roomID):
    if 'user' in session and Chatroom.query.filter_by(id=roomID).first():
        session['user']['activeRoom'] = roomID
        session.modified = True
        return render_template("room.html", room=roomInfo(session['user'], roomID))
    else:
        return redirect(url_for("main"))   
  
#Create a chatroom    
@app.route('/createRoom', methods=["POST"])
def createRoom():
    if request.json['name'] and 'user' in session:
        if Chatroom.query.filter_by(name= request.json['name']).first():
            return 'Success'
        else:
            room = Chatroom(session['user']['id'], request.json['name'])
            db.session.add(room)
            db.session.commit()
            return 'Success'
    else:
        return 'Failure'
      
#delete a chatroom      
@app.route('/deleteRoom/<int:roomID>', methods=["POST"])
def deleteRoom(roomID):
    if 'user' in session:
        roomExists = Chatroom.query.filter(and_(Chatroom.ownerID == session['user']['id'], Chatroom.id == roomID,)).first()
        if roomExists:
            room = Chatroom.query.filter_by(id=roomID).first()
            deleteMessagesFromRoom(roomID)
            db.session.delete(room)
            db.session.commit()
            return 'Success'
    return 'Failure'
   
#exit the chatroom   
@app.route('/exitRoom/<int:roomID>', methods=['POST'])
def exitRoom(roomID):
    if 'user' in session and Chatroom.query.filter_by(id=roomID).first():
        session['user']['activeRoom'] = -1
        session.modified = True
        return '/main'
    else:
        return 'Failure'
    
#poll chatrooms to get an updated list of all chatrooms    
@app.route('/pollRooms', methods=["GET"])
def pollRooms():
    if 'user' in session:
        jsonRooms = json.dumps(getAllRooms(session['user']['id']))
        return jsonRooms
    else:
        return 'Failure'
 
#send a message
@app.route('/send/<int:roomID>', methods=["POST"])
def send(roomID):
    if 'user' in session:
        if 'message' in request.json:
            sent = sendMessage(roomID, request.json['message'], session['user'])
            if sent:
                return 'Success'
    return 'Failure' 
        
#Get messages for a chat room or redirt to correct room/home
@app.route('/getMessages/<int:roomID>', methods=["POST"])
def getMessages(roomID):
    if 'user' in session and 'latestMessage' in request.json:
        if session['user']['activeRoom'] == -1:
            
            return json.dumps({
                'redirect': '/main'
            })
        if roomID != session['user']['activeRoom']:
            return json.dumps({
                'redirect': '/room/'+str(session['user']['activeRoom'])
            })
        elif (Chatroom.query.filter_by(id=roomID).first()):
            a = getMessagesSince(roomID, request.json['latestMessage'])
            return json.dumps(a)
        else:
            return json.dumps({
                'error': 'Room has been deleted'
            })

    return redirect(url_for('main'))       
        
      
#########################################   Helper Functions   #################################################
 
#Return user session object for home/list of chatrooms
def populateSession(usr):
    myRooms = [r.as_dict() for r in Chatroom.query.filter_by(ownerID=usr['id']).all()]
    for x in myRooms:
        del x['ownerID']

    otherRooms = [a.as_dict() for a in Chatroom.query.filter(Chatroom.ownerID != usr['id']).all()]
    for r in otherRooms:
        ownerName = User.query.filter_by(id=r['ownerID']).first().name
        r['ownerName'] = ownerName
        del r['ownerID']

    return {
        'id': usr['id'],
        'name': usr['name'],
        'myRooms': myRooms,
        'otherRooms': otherRooms
    }
  
#Return room session object for chatroom  
def roomInfo(user, roomID):
    room = (Chatroom.query.filter_by(id=roomID).first()).as_dict()
    return {
        'id': room['id'],
        'ownerID': room['ownerID'],
        'roomName': room['name'],
        'senderName': user['name'],
        'senderID': user['id']
    }

#get the user's rooms and the other rooms
def getAllRooms(userID):
    myRooms = [m.as_dict() for m in Chatroom.query.filter_by(ownerID=userID).all()]
    for room in myRooms:
        del room['ownerID']

    otherRooms = [r.as_dict() for r in Chatroom.query.filter(Chatroom.ownerID != userID).all()]
    for room in otherRooms:
        ownerName = User.query.filter_by(id=room['ownerID']).first().name
        room['ownerName'] = ownerName
        del room['ownerID']

    return {
        'myRooms': myRooms,
        'otherRooms': otherRooms
    }
    
def sendMessage(roomID, message, user):
    try:
        message = Message(roomID, user['id'], user['name'], message, datetime.utcnow())
        db.session.add(message)
        db.session.commit()
        return True
    except IntegrityError:
        flash('Sorry, that message could not be sent.')
        return False
  
#Function to delete messages associated with the room which was just deleted.  
def deleteMessagesFromRoom(roomID):
    deleteMsgs = Message.query.filter(Message.roomID == roomID).all()
    for m in deleteMsgs:
        db.session.delete(m)
    db.session.commit()

#Get all messages since the latest message in the chat. -1 if chat just joined so get all
def getMessagesSince(roomID, latestMessage):
    if db.session.query(Message.id).count() == 0:
        return {
            'newMessages': {},
            'latestMessage': 0
        }

    allMessages = Message.query.filter(Message.roomID == roomID, Message.id > latestMessage).all()
    
    newMessages = [m.as_dict() for m in allMessages]

    for x in newMessages:
        x['time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        del x['roomID']
        if x['id'] > latestMessage:
            latestMessage = x['id']

    return {
        'newMessages': newMessages,
        'latestMessage': latestMessage
    }
    
    
if __name__ == '__main__':
    app.run()
