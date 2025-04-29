from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.String(500))
    bot_reply = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100))
    event_date = db.Column(db.DateTime)
    event_description = db.Column(db.String(500))