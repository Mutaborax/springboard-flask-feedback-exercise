from getpass import getpass
from app import app, db
from models import User, Feedback

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create sample users
    u1 = User.register("user1", getpass(
        "Enter password for user1: "), "email1@example.com", "First1", "Last1")
    u2 = User.register("user2", getpass(
        "Enter password for user2: "), "email2@example.com", "First2", "Last2")

    db.session.add_all([u1, u2])
    db.session.commit()

    # Create sample feedbacks
    f1 = Feedback(title="Feedback 1",
                  content="This is feedback 1", user_id=u1.id)
    f2 = Feedback(title="Feedback 2",
                  content="This is feedback 2", user_id=u2.id)

    db.session.add_all([f1, f2])
    db.session.commit()
