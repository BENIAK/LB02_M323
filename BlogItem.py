from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BlogItem(db.Model):
    __tablename__ = 'blog_items'
    item_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
