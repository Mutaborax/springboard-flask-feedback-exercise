from forms import FeedbackForm
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from models import db, User, Feedback
from forms import RegisterForm, LoginForm, LogoutForm

app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://127.0.0.1/flaskFeedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
db.init_app(app)

# Define the LogoutForm class


class LogoutForm(FlaskForm):
    pass
# Index route redirects to the register route


@app.route('/')
def index():
    return redirect('/login')

# Register route for handling registration form


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data

        user_exists = User.query.filter(
            (User.username == username) | (User.email == email)).first()
        if user_exists:
            flash("User with this username or email already exists", 'danger')
            return render_template('register.html', form=form)

        user = User.register(
            username=username,
            password=form.password.data,
            email=email,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect(f'/users/{user.username}')

    return render_template('register.html', form=form)


# Login route for handling login form


@ app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            # Use url_for instead of string concatenation
            return redirect(f'/users/{user.username}')
        else:
            flash("Invalid username or password", 'danger')
    return render_template('login.html', form=form)

# User detail route to display user information


@ app.route('/users/<username>', methods=['GET'])
def user_detail(username):
    # Ensure that only the logged in user can view this page
    if 'username' not in session or session['username'] != username:
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    return render_template('user_detail.html', user=user)


@ app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    # Ensure that only the logged in user can delete their account
    if 'username' not in session or session['username'] != username:
        return redirect('/')
    user = User.query.filter_by(username=username).first()
    # Delete all of user's feedback
    Feedback.query.filter_by(user_id=user.id).delete()
    # Delete user
    db.session.delete(user)
    db.session.commit()
    # Clear user information in the session
    session.clear()
    return redirect('/')


@ app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    form = FeedbackForm()
    if form.validate_on_submit():
        if 'username' in session and session['username'] == username:
            user = User.query.filter_by(username=username).first()
            feedback = Feedback(title=form.title.data,
                                content=form.content.data, user_id=user.id)
            db.session.add(feedback)
            db.session.commit()
            return redirect(f'/users/{username}')
    return render_template('feedback/add.html', form=form)


@ app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        # Ensure that only the user who has written the feedback can update it
        if 'username' in session and session['username'] == feedback.user.username:
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            return redirect(f'/users/{feedback.user.username}')
    return render_template('feedback/update.html', form=form)


@ app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    # Ensure that only the user who has written the feedback can delete it
    if 'username' in session and session['username'] == feedback.user.username:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.user.username}')
    return redirect('/')


@ app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash("You have been logged out.", 'success')
    return redirect('/')


@ app.context_processor
def inject_logout_form():
    return dict(logout_form=LogoutForm())


if __name__ == '__main__':
    app.run(debug=True)
