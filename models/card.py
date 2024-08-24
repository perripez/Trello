from init import db, ma
from marshmallow import fields

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String)
    priority = db.Column(db.String)
    date = db.Column(db.Date) # Created Date (when the card was created)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship('User', back_populates='cards')
    # User can have many cards
    comments = db.relationship('Comment', back_populates='card', cascade="all, delete")
    # Single card can have many comments

class CardSchema(ma.Schema):
    user = fields.Nested('UserSchema', only=["id", "name", "email"])
    comments = fields.List(fields.Nested('CommentSchema', exclude=["card"]))

    class Meta:
        fields = ("id", "title", "description", "status", "priority", "date", "user", "comments")
        ordered = True

card_schema = CardSchema()
cards_schema = CardSchema(many=True)