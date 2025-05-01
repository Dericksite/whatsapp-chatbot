from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from models.conversation import Conversation
from flask_login import login_required
from models import db
from datetime import datetime


conversation_bp = Blueprint('conversation', __name__)

@conversation_bp.route('/conversation')
@login_required
def conversation():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    print("page => ", page, search)

    query = Conversation.query
    if search:
        query = query.filter(Conversation.phone_from.like(f'%{search}%'))

    # conversations = Conversation.query.all()
    conversations = query.order_by(Conversation.created_at.asc()).paginate(page=page, per_page=10)

    return render_template('conversation_history.html', conversations=conversations)


@conversation_bp.route('/conversation/<int:id>')
@login_required
def view(id):
    conversation = Conversation.query.get(id)
    return render_template('conversation_view.html', conversation=conversation)



# Route for creating a new conversation
@conversation_bp.route('/conversation/create', methods=['POST'])
def create():
    data = request.get_json()  # Get the JSON data from the request
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Extract data from the JSON request body
    phone_from = data.get('phone_from')
    phone_to = data.get('phone_to')
    message = data.get('message')

    # Validate required fields
    if not phone_from or not phone_to or not message:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create a new conversation object
    new_conversation = Conversation(
        phone_from=phone_from,
        phone_to=phone_to,
        message=message,
        created_at=datetime.now()  # Use the current timestamp
    )

    # Add the new conversation to the session and commit to save it in the database
    db.session.add(new_conversation)
    db.session.commit()

    return jsonify({'message': 'Conversation created successfully!', 'conversation': new_conversation.id}), 201
    

@conversation_bp.route('/conversation/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    conversation = Conversation.query.get(id)
    if conversation:
        db.session.delete(conversation)
        db.session.commit()
        flash('Conversation deleted successfully!', 'success')
    else:
        flash('Conversation not found.', 'danger')
    return redirect(url_for('conversation.conversation'))