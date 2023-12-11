from database.models import Product, Order, Product
from . import celery


@celery.task(name='send_monthly_report')
def export_product_as_csv(product_id):
    product = Product.query.filter_by(id=product_id).first()
    orders = Order.query.filter_by(product_id=product_id).all()
    products_sold = len(orders)
    with open('/static/products/{}.csv'.format(product.id), 'w') as f:
        f.write('Product ID, Product Name, Product Rate, Product Unit, Current Stock, Sold Quantity\n')
        f.write('{},{},{},{},{},{}\n'.format(product.id, product.name, product.rate, product.unit, product.current_stock, products_sold + " {}s".format(product.unit) if product.unit != "kg" else products_sold + " {}s".format(product.unit)))
    return True
