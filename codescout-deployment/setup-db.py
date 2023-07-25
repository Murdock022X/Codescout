from website import create_app, models

def main():
    app = create_app()

    with app.app_context():
        models.db.drop_all()
        models.db.create_all()
        models.db.session.commit()

if __name__ == '__main__':
    main()