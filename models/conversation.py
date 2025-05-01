from . import db

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_from = db.Column(db.String(15), nullable=False)
    phone_to = db.Column(db.String(15), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    
    # user = db.relationship('User', backref=db.backref('conversations', lazy=True))

    def __repr__(self):
        return f'<Conversation {self.id}>'
