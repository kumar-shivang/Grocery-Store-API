from database.models import Product, Order, Product
from . import celery


@celery.task
def export_product_as_csv(product_id):
    product = Product.query.filter_by(id=product_id).first()
    orders = Order.query.filter_by(product_id=product_id).all()
    products_sold = len(orders)
    with open('static/products/{}.csv'.format(product.id), 'w') as f:
        f.write('Product ID, Product Name, Product Rate, Product Unit, Current Stock, Sold Quantity\n')
        f.write('{},{},{},{},{},{}\n'.format(product.id, product.name, product.rate, product.unit, product.current_stock,  products_sold))
    print('exported product {}'.format(product_id))
    return True
