from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.bot_setting import BotSetting
from flask_login import login_required
from models import db

botSetting_bp = Blueprint('botSetting', __name__)

@botSetting_bp.route('/bot-setting', methods=['GET', 'POST'])
@login_required
def bot_setting():
    setting = BotSetting.query.first()  # Fetch the first settings
    if request.method == 'POST':
        # Get updated form data
        setting.site_name = request.form['site_name']
        setting.service_description = request.form['service_description']
        setting.service_price = request.form['service_price']
        setting.business_time = request.form['business_time']
        setting.delivery = request.form['delivery']

        # Commit the changes to the database
        db.session.commit()

        flash('Bot setting updated successfully!', 'success')
        return redirect(url_for('botSetting.bot_setting'))  # Redirect to view page after update


    return render_template('bot_setting.html', setting=setting)