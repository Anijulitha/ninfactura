from __init__ import create_app

app = create_app()

if _name_ == '__main__':
    with app.app_context():
        from models import db
        db.create_all()
    app.run(debug=True)
