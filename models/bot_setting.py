from . import db

class BotSetting(db.Model):
    __tablename__ = 'bot_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(255), nullable=False)
    service_description = db.Column(db.Text, nullable=True)
    service_price = db.Column(db.Float, nullable=False)
    opening_time = db.Column(db.String(10), nullable=False)
    closing_time = db.Column(db.String(10), nullable=False)
    pickup_days = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<BotSetting {self.site_name}>'