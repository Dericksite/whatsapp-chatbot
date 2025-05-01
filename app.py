from flask import Flask
from config import Config
from models import db
from models.user import User
from flask_login import LoginManager
from controllers import auth_bp, main_bp, conversation_bp, botSetting_bp
import os
from dotenv import load_dotenv
from flask_migrate import Migrate


load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)


# Initialize the database
db.init_app(app)


migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

# Define the user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = 'auth.login'  # Redirect here if not logged in

# Register Blueprints (Controllers)
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(conversation_bp)
app.register_blueprint(botSetting_bp)



PORT = os.getenv("PORT")
if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=80) # server
    # app.run(port=PORT)    # localhost
    app.run(debug=True)
