"""Lama Log."""

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

import time 
import datetime

from NeuroPy import NeuroPy
from model import connect_to_db, db, Session, State, User
from collect import collect

app = Flask(__name__)

# This is required to use Flask sessions and debug toolbar.
app.secret_key = "kugel"

         
##############################################################################

@app.route('/')
def main():
    """Homepage"""

    return render_template("homepage.html")

@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")

@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    new_user = User(email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % email)
    return redirect("/")

@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")

@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.get_user_by_email(email)
    # user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")

    return redirect("/users/%s" % user.user_id)

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")

@app.route('/eeg-states.json')
def eeg_states_data():
    """Return time series data of EEG States."""
    # Look up current_user with Flask
    # current_user.session....
    # from session, query all the states

    all_states = State.query.filter_by(session_id=1).all()
    # TODO: Can improve this query to get all the sessions for one user and 
    # make a graph for each session. 

    # List comprehensions to feed into data_dictionary.
    meditation = [state.meditation for state in all_states]
    attention = [state.attention for state in all_states]
    labels = [datetime.datetime.strftime(state.utc, "%-M:%-S") for state in all_states]
    # Using strftime to account for jsonifying.

    data_dict = {
        "labels": labels,
        "datasets": [
            {
                "label": "Meditation",
                "fillColor": "rgba(220,220,220,0.2)",
                "strokeColor": "rgba(220,220,220,1)",
                "pointColor": "rgba(220,220,220,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(220,220,220,1)",
                "data": meditation
            },
            {
                "label": "Attention",
                "fillColor": "rgba(151,187,205,0.2)",
                "strokeColor": "rgba(151,187,205,1)",
                "pointColor": "rgba(151,187,205,1)",
                "pointStrokeColor": "#fff",
                "pointHighlightFill": "#fff",
                "pointHighlightStroke": "rgba(151,187,205,1)",
                "data": attention
            }
        ]
    }
    return jsonify(data_dict)


@app.route("/users/<int:user_id>")
def user_detail(user_id):
    """Show info about user."""

    user = User.query.get(user_id)
    return render_template("user.html", user=user)



##############################################################################
if __name__ == "__main__":

    app.debug = True
    connect_to_db(app)
    DebugToolbarExtension(app)
    app.run()
