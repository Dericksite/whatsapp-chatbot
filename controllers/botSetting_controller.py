from flask import Blueprint, render_template
from models.bot_setting import BotSetting
from flask_login import login_required

botSetting_bp = Blueprint('botSetting', __name__)

@botSetting_bp.route('/bot-setting')
@login_required
def bot_setting():
    setting = BotSetting.query.first()  # Fetch the first settings
    return render_template('bot_setting.html', setting=setting)