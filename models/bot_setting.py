from . import db

class BotSetting(db.Model):
    __tablename__ = 'bot_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(255), nullable=False)
    service_description = db.Column(db.Text, nullable=False)
    service_price = db.Column(db.Text, nullable=False)
    business_time = db.Column(db.Text, nullable=False)
    delivery = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<BotSetting {self.site_name}>'