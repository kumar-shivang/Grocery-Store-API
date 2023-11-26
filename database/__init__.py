from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_database(app):
    from .models import User, Product, Category, Order, Role, ProductImage
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.commit()
        print("Database initialized")

        if not Role.query.filter_by(role_name='admin').first():
            admin_role = Role('admin', 'Administrator : Can manage categories and products')
            db.session.add(admin_role)
            db.session.commit()
            print("Admin role created")

        if not Role.query.filter_by(role_name='user').first():
            user_role = Role('user', 'User : Can place orders')
            db.session.add(user_role)
            db.session.commit()
            print("User role created")

        if not Role.query.filter_by(role_name='manager').first():
            manager_role = Role('manager', 'Manager : Can manage products and reqeust to add new categories')
            db.session.add(manager_role)
            db.session.commit()
            print("Manager role created")

        if not User.query.filter_by(username='admin').first():
            admin = User('admin', 'Password123', 'admin@localhost', Role.query.filter_by(role_name='admin').first().id)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created")
            print("Admin Username: admin")
            print("Admin Password: \033[91m{}\033[0m".format('Password123'))

        if not Category.query.filter_by(category_name='Uncategorized').first():
            uncategorized = Category('Uncategorized', 'Default category for products')
            db.session.add(uncategorized)
            db.session.commit()
            print(f"Uncategorized category created with id {uncategorized.id}")

        if not ProductImage.query.filter_by(image_name='default.png').first():
            default_image = ProductImage('default.png')
            db.session.add(default_image)
            db.session.commit()
            print(f"Default image created with id {default_image.id}.")
