"""Models and database functions for EEG tracking project."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

##############################################################################
# Model definitions

class User(db.Model):
    """User of lama log website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    sessions = db.relationship("Session", order_by="Session.utc")



    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" (self.user_id, self.email)

    @classmethod
    def get_user_by_id(cls, uid):
        return cls.query.filter_by(user_id=uid).first()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()



class Session(db.Model):
    """Running time of a session."""
    
    __tablename__ = "sessions"
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    utc = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    # Link to intermediary table that is states. Map one session to multiple states.
    # And one user maps to multiple sessions.
    states = db.relationship("State", order_by="State.utc")
    meditation_high_score = db.Column(db.Integer)

    def generate_high_score(self):
        """Generates high meditation score and stores it in meditation_high_score."""
        
        selection = self.states

        attn = []
        med = []
        for point in selection:
            if point.attention !=0:
                attn.append(point.attention)
            if point.meditation !=0:
                med.append(point.meditation)

        att_avg = sum(attn)/len(attn)
        med_avg = sum(med)/len(med)
        zen_score = abs(att_avg - med_avg)

        self.meditation_high_score = zen_score

    # def __repr__(self):
    #     return "<UTC:%s>" % (self.utc)


class State(db.Model):
    """Cognition values."""
    
    __tablename__ = "states"
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    utc = db.Column(db.DateTime, nullable=True)
    attention = db.Column(db.Integer, nullable=True)
    meditation = db.Column(db.Integer, nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))


    def __repr__(self):
        return "<UTC:%s, Attention:%d, Meditation:%d>" % (self.utc, self.attention, self.meditation)

    


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lamalog.db'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app    
    db.init_app(app)


if __name__ == "__main__":
    from server import app
    connect_to_db(app)
    print "Connected to DB."
