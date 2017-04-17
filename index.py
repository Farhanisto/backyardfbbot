
import json
import requests
from flask import Flask,render_template,url_for,request,redirect,flash
from datetime import datetime
from Forms import BackyardForm
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import desc


baseddir=os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.abspath('static/img')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app=Flask(__name__)
app.config['SECRET_KEY']='\xa2}{a9\xf8\x08-\x92 \xcb\x81E\xc7/\xd9\x9a\x9b\xa2^\xb4 !A'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(baseddir,'backyard.db')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db=SQLAlchemy(app)

#models class
class Backyard(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    photo_url=db.Column(db.String(300),nullable=False)
    date=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
    description=db.Column(db.String(300),nullable=False)
    location=db.Column(db.String(300),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

    @staticmethod
    def newest(num):

        return Backyard.query.order_by(desc(Backyard.date)).limit(num)


    def __repr__(self):
        return "<Bookmark '{}':'{}'>".format(self.description,self.photo_url)



class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user=db.Column(db.String(80),unique=True,nullable=False)
    email=db.Column(db.String(80))
    backyards = db.relationship('Backyard', backref='user', lazy='dynamic')



    def __repr__(self):
        return "<Bookmark %r"%self.user


#backyard instance to store information from facebook
backyard = Backyard()




def loged_in_user(user_id):
   return User.query.filter_by(user=user_id).first()


# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
GATE = 'EAAEVjnwxwgYBAKGvcxJ3DBjIj2ZCa1laA2MIBzJfKZCiFePd2hqpP8cX9w0ZBcZB9grlWlz4xfQc4LReDUmTIDEHZCSndmvP9adyZC0kLgB26uKREEu3wZBuBwLZB2XXgEYfZAuZC8D4QFzFtPO0aonZC0u1UocEZCYoF4o6ZBS9pzDjCGwZDZD'


def button_template(sender):
    return {
  "recipient":{
    "id":sender
  },
  "message":{
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text":"Hy am Bob, Ill be guiding you in simplifying your backyard sales.Select one of the options below ",
        "buttons":[
          {
            "type":"postback",
            "title":"Sell an Item",
            "payload":"SALE_PAYLOAD",
          },
          {
            "type":"postback",
            "title":"View/Buy an Item",
            "payload":"BUY_PAYLOAD"
          }
        ]
      }
    }
  }
}

def buy_list_template(sender):
    try:
        by = Backyard.newest(5)
        print "hellllllo"
        print by
        photo = []
        description = []
        user = []
        for data in by:
            photo.append(data.photo_url)
            description.append(data.description)
            user.append(data.user.user)
        print photo
        print description
        print user
        return {
            "recipient": {
                "id": sender
            }, "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": str(description[0]),
                                "image_url": str(photo[0]),
                                "subtitle": "Message the owner",
                                "default_action": {
                                    "type": "web_url",
                                    "url": 'https://7f6219d8.ngrok.io/add?user=' + str(user[0]),

                                },
                                "buttons": [
                                    {
                                        "title": "View",
                                        "type": "web_url",
                                        "url": str(photo[0]),

                                    }
                                ]
                            },
                            {
                                "title": "Classic White T-Shirt",
                                "image_url": "https://peterssendreceiveapp.ngrok.io/img/white-t-shirt.png",
                                "subtitle": "100% Cotton, 200% Comfortable",
                                "default_action": {
                                    "type": "web_url",
                                    "url": "https://peterssendreceiveapp.ngrok.io/view?item=100",

                                },
                                "buttons": [
                                    {
                                        "title": "Shop Now",
                                        "type": "web_url",
                                        "url": "https://peterssendreceiveapp.ngrok.io/shop?item=100",

                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    except IndexError:
        print "no items on sale currently. Try again later"
        farhan(GATE, sender,"no items on sale currently. Try again later")




def location_quick_reply(sender):
    return {
        "recipient": {
            "id": sender
        },
        "message": {
            "text": "Share the location you want to sell this item:",
            "quick_replies": [
                {
                    "content_type": "location",
                }
            ]
        }
    }


@app.route("/login",methods=["POST","GET"])

def login():
    return render_template('login.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/add",methods=["POST","GET"])

def add():


    form=BackyardForm()
    recipient=request.args.get('user')
    if form.validate_on_submit():
        comment = form.comment.data
        farhan(GATE,recipient,comment)
        print 'save comment to db'
        flash("Your message has been sent")


    return render_template('add.html',form=form)


@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'my_secret_key':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    return "Verification failed!"

@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  payload = request.get_data()
  print payload
  for sender, message in messaging_events(payload):
    print "Incoming from %s: %s" % (sender, message)
    send_message(GATE, sender, message)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]

  for event in messaging_events:
    sender = event['sender']['id']
    if "message" in event and "text" in event["message"]:
      if str(event['message']['text']).startswith('Description'):
          print 'Capture users Description of item here'
          description=event['message']['text']
          backyard.description=description
          print backyard.photo_url
          print backyard.description
          print description
          payload = location_quick_reply(sender)
          r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + GATE, json=payload)

      else:

          payload = button_template(sender)
          print payload
          r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + GATE, json=payload)
          print r


    elif 'postback' in event and 'payload' in event['postback']:
        sender = event['sender']['id']
        if event['postback']["payload"]=='User_defined':
            print 'hy'

            payload = button_template(sender)  # {'recipient': {'id': sender}, 'message': {'text': "Hello World"}}
            print payload
            r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + GATE, json=payload)
            print r
        elif event['postback']["payload"]=='BUY_PAYLOAD':
            print "captured"

            payload = buy_list_template(sender)  # {'recipient': {'id': sender}, 'message': {'text': "Hello World"}}
            print payload
            r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + GATE, json=payload)
            print r

        elif event['postback']["payload"]=='SALE_PAYLOAD':
            print "captured"
            message="Step 1: Send us a photo of item you want to sell"
            yield event["sender"]["id"], message.encode('unicode_escape')

    elif 'message' in event and 'payload' in event['message']['attachments'][0]:
        print 'well done'
        if 'title' in event['message']['attachments'][0] and 'elements' not in event['message']['attachments'][0]['payload']:
            location = event['message']['attachments'][0]['title']
            backyard.location=location
            print backyard.photo_url
            print backyard.description
            print location

            #add user id to db
            user_id=event["sender"]["id"]
            if not loged_in_user(user_id):
                user = User(user=user_id, email='farhano@gmail.com')
                db.session.add(user)
                db.session.commit()
            by = Backyard(user=loged_in_user(user_id),photo_url=backyard.photo_url, date=datetime.utcnow(), description=str(backyard.description),location=str(backyard.location))

            print by.photo_url
            print by.description
            print by.location
            db.session.add(by)
            db.session.commit()
            print "Thank you...Uploaded to db"
            message = "Your Item has been Created. Seat back and wait to be messaged by one of facebooks 1 billion clients. Thanks :)"
            yield event["sender"]["id"], message.encode('unicode_escape')

        if 'url' in event['message']['attachments'][0]['payload']:
            print 'yay image capt'
            image_path = event['message']['attachments'][0]['payload']['url']
            backyard.photo_url=image_path
            print backyard.photo_url
            print image_path
            item_description = "Step 2: Describe this item,start this with the word 'Description'."
            send_message(GATE, event['sender']['id'], item_description.encode('unicode_escape'))

def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.encode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

@app.errorhandler(404)
def errorHandler(e):
	return render_template('404.html'),404

#function to send message to user automatically

def farhan(token, recipient,text):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": token},
                      data=json.dumps({
                          "recipient": {"id": recipient},
                          "message": {"text": text.encode('unicode_escape')}
                      }),
                      headers={'Content-type': 'application/json'})

farhan(GATE,'1089993001113019','hello farhan bot')



if __name__ == '__main__':
  app.run(debug=True)