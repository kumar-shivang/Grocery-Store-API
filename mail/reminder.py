from scheduled_jobs import celery
from . import mail, send_mail
from database.models import User, Order, Role
import pyhtml as h
from datetime import datetime, timedelta, date


def reminder1(username):
    msg = h.html(
        h.head(
            h.h1('Reminder')
        ),
        h.body(
            h.h1('Reminder'),
            h.p('Your cart is empty'),
            h.p('Please add items to your cart'),
            h.p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def reminder2(username, no_of_items):
    msg = h.html(
        h.head(
            h.h1('Reminder')
        ),
        h.body(
            h.h1('Reminder'),
            h.p('Your cart has ', no_of_items, ' items'),
            h.p('Please checkout'),
            h.p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


@celery.task(name='send_reminder_mail')
def send_reminder_mail():
    user_role = Role.query.filter_by(role_name='user').first()
    users = User.query.filter_by(role_id=user_role.id).all()
    for user in users:
        orders = Order.query.filter_by(user_id=user.id, confirmed=False).all()
        if len(orders) == 0:
            send_mail(subject='Grocery app reminder',
                      sender="reminder@grocery.com",
                      recipients=[user.email],
                      html_body=reminder1(user.username))
        else:
            send_mail(subject='Grocery app reminder',
                      sender="reminder@grocery.com",
                      recipients=[user.email],
                      html_body=reminder2(user.username, len(orders)))
    print('mail sent')


def monthly_reminder1(username):
    msg = h.html(
        h.head(
            h.h1('We missed you')
        ),
        h.body(
            h.p('Dear {}'.format(username)),
            h.p('You have not placed any orders this month'),
            h.p('Please place an order'),
            h.p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def monthly_reminder2(username):
    msg = h.html(
        h.head(
            h.h1('We are waiting for you')
        ),
        h.body(
            h.p('Dear {}'.format(username)),
            h.p('You have placed orders this month'),
            h.p('Please checkout'),
            h.p('Thank you for using grocery store.')
        )
    )
    return msg.render()


def monthly_reminder3(username, no_of_confirmed, no_of_unconfirmed, value_of_confirmed):
    msg = h.html(
        h.head(
            h.h1('We are waiting for you')
        ),
        h.body(
            h.p('Dear {}'.format(username)),
            h.p('You have placed {} orders this month'.format(no_of_confirmed + no_of_unconfirmed)),
            h.p('You have confirmed {} orders this month'.format(no_of_confirmed)),
            h.p('You have unconfirmed {} orders this month'.format(no_of_unconfirmed)),
            h.p('The total value of confirmed orders is {}'.format(value_of_confirmed)),
            h.p('Please checkout'),
            h.p('Thank you for using grocery store.')
        )
    )
    return msg.render()


def monthly_reminder4(username, no_of_confirmed, value_of_confirmed):
    msg = h.html(
        h.head(
            h.h1('We are waiting for you')
        ),
        h.body(
            h.p('Dear {}'.format(username)),
            h.p('You have placed {} orders this month'.format(no_of_confirmed)),
            h.p('The total value of confirmed orders is {}'.format(value_of_confirmed)),
            h.p('Thank you for using grocery store.')
        )
    )
    return msg.render()


@celery.task(name='send_monthly_report')
def send_monthly_report():
    user_role = Role.query.filter_by(role_name='user').first()
    users = User.query.filter_by(role_id=user_role.id).all()
    for user in users:
        today = date.today()
        one_month_ago = today - timedelta(days=30)
        orders = Order.query.filter_by(user_id=user.id).filter(Order.order_time > one_month_ago).all()
        confirmed = [order for order in orders if order.confirmed]
        unconfirmed = [order for order in orders if not order.confirmed]
        if len(orders) == 0:
            send_mail(subject='Grocery app reminder',
                      sender="report@.grocery.com",
                      recipients=[user.email],
                      html_body=monthly_reminder1(user.username))
        elif len(confirmed) == 0 and len(unconfirmed) > 0:
            send_mail(subject='Grocery app reminder',
                      sender="report@.grocery.com",
                      recipients=[user.email],
                      html_body=monthly_reminder2(user.username))
        elif len(confirmed) > 0 and len(unconfirmed) > 0:
            no_of_confirmed = len(confirmed)
            no_of_unconfirmed = len(unconfirmed)
            value_of_confirmed = sum([order.value for order in confirmed])
            send_mail(subject='Grocery app reminder',
                      sender="report@.grocery.com",
                      recipients=[user.email],
                      html_body=monthly_reminder3(user.username, no_of_confirmed, no_of_unconfirmed,
                                                  value_of_confirmed))
        elif len(confirmed) > 0 and len(unconfirmed) == 0:
            no_of_confirmed = len(confirmed)
            value_of_confirmed = sum([order.value for order in confirmed])
            send_mail(subject='Grocery app reminder',
                      sender="report@.grocery.com",
                      recipients=[user.email],
                      html_body=monthly_reminder4(user.username, no_of_confirmed, value_of_confirmed))
    print('mail sent')
