from website import create_app, models

def main():

    # Generate app and use app context with SQL config to create the tables in 
    # the appropriate database.
    app = create_app()
    with app.app_context():
        models.db.drop_all()
        models.db.create_all()
        models.db.session.commit()

        app.logger.info('Database setup complete.')

if __name__ == '__main__':
    main()