from flask import Blueprint, render_template
from models.conversation import Conversation
from flask_login import login_required

conversation_bp = Blueprint('conversation', __name__)

@conversation_bp.route('/conversations')
@login_required
def history():
    conversations = Conversation.query.all()
    return render_template('conversation_history.html', conversations=conversations)

@conversation_bp.route('/conversations/<int:id>')
@login_required
def view(id):
    conversation = Conversation.query.get(id)
    return render_template('conversation_view.html', conversation=conversation)
