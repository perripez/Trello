from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.comment import Comment, comment_schema, comments_schema
from models.card import Card

comments_bp = Blueprint("comments", __name__, url_prefix="/<int:card_id>/comments")

# /<int:card_id>/comments/ - GET: no need to define

# Create the comment route
@comments_bp.route("/", methods=["POST"])
@jwt_required()
def create_comment(card_id):
    # get the comment message from the request body
    body_data = request.get_json()
    # fetch the card with id=card_id
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card exists, create an instance of the comment model
    if card: 
        comment = Comment(
            message = body_data.get("message"),
            date = date.today(),
            card = card,
            user_id = get_jwt_identity()
        )
    # add and commit the session
        db.session.add(comment)
        db.session.commit()
    # return acknowledgement message
        return comment_schema.dump(comment), 201
    # else, returm error
    else:
        return {"error": f"Card with id {card_id} not found"}, 404
    
# /<int:card_id>/comments/comment_id - DELETE
@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(card_id, comment_id):
    # fetch the comment from the db
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    # if comment exists, delete the comment + return acknowledgement
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return {"message": f"Comment '{comment.message}' deleted successfully!"}
    # else, return error message
    else:
        return {"error": f"Comment with id {comment_id} not found"}, 404

# /<int:card_id>/comments/comment_id - UPDATE
@comments_bp.route("/<int:comment_id>", methods=["PATCH"])
@jwt_required()
def update_comment(card_id, comment_id):
    # get the info from the body of the request
    body_data = request.get_json()
    # get the comment from the db
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    # if the comment exists, upgrade the fields as required + return acknowledgement
    if comment:
        comment.message = body_data.get("message") or comment.message
        db.session.commit()
        return comment_schema.dump(comment)
    # else, return error message
    else:
        return {"error": f"Comment with id {comment_id} not found"}