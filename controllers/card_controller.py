from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, card_schema, cards_schema

from controllers.comment_controller import comments_bp

from utils.utils import auth_as_admin_decorator

cards_bp = Blueprint("cards", __name__, url_prefix="/cards")
cards_bp.register_blueprint(comments_bp)

# /cards - GET: Fetch all cards
@cards_bp.route("/")
def get_all_cards():
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return cards_schema.dump(cards)

# /cards/<id> - GET: Fetch a specific card
@cards_bp.route("/<int:card_id>")
def get_a_card(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        return card_schema.dump(card)
    else:
        return {"error": f"Card with id {card_id} not found"},404

# /cards - POST: Create a new card
@cards_bp.route("/", methods=["POST"])
@jwt_required()
@auth_as_admin_decorator
def create_card():
    # get the data from the body of the request
    body_data = card_schema.load(request.get_json())
    # create a new card model instance
    card = Card(
        title = body_data.get("title"),
        description = body_data.get("description"),
        date = date.today(),
        status = body_data.get("status"),
        priority = body_data.get("priority"),
        user_id = get_jwt_identity()
    )
    # add and commit to the db
    db.session.add(card)
    db.session.commit()
    # send a response message
    return card_schema.dump(card)

# /cards/<id> - DELETE: Delete a card
@cards_bp.route("/<int:card_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_decorator
def delete_card(card_id):
    #check whether user is admin or not
    # is_admin = authorise_as_admin()
    # if not admin, return error message
    if not is_admin:
        return {"error": "User is not authorised to perform this action"}

    # fetch the card from the db
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card exists, delete card + return acknowledgement
    if card:
        db.session.delete(card)
        db.session.commit()
        return {"message": f"Card {card.title} deleted successfully!"}
    # else, return error message
    else:
        return {"error": f"Card with id {card_id} not found"}, 404

# /cards/<id> - PUT, PATCH: Edit a card entry
@cards_bp.route("/<int:card_id>", methods=["PATCH","PUT"])
@jwt_required()
@auth_as_admin_decorator
def update_card(card_id):
    # get the info from the body of the request
    body_data = card_schema.load(request.get_json(), partial=True)
    # get the card from the db
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # check if the user is admin or not
    # is_admin = authorise_as_admin()
    
    # if the card exists, update the fields as required + return acknowledgement
    if card:
     # if the user is not the owner of the card
        if not is_admin and str(card.user_id) != get_jwt_identity():
        # return error message
            return {"error": "Cannot perform this operation. Only the card owner can perform operation"}

        card.title = body_data.get("title") or card.title
        card.description = body_data.get("description") or card.description
        card.status = body_data.get("status") or card.status
        card.priority = body_data.get("priority") or card.priority
        # commit to db
        db.session.commit()
        return card_schema.dump(card)
    # else, return error message
    else:
        return {"error": f"Card with id {card_id} not found."}, 404
