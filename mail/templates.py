from pyhtml import *


def manager_created(username:str):
    msg = html(
        head(
            h1('Manager Created')
        ),
        body(
            h1('Manager Request Created'),
            p('Your request has been created successfully, wait for approval'),
            p('Your username is: ', username),
            p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def manager_approved(user_id:int, username:str):
    msg = html(
        head(
            h1('Manager Approved')
        ),
        body(
            h1('Manager Request Approved'),
            p('Your request has been approved successfully'),
            p('Your username is: ', username),
            p('Your user id is: ', user_id),
            p('You can now login to the system'),
            p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def manager_rejected():
    msg = html(
        head(
            h1('Manager Rejected')
        ),
        body(
            h1('Manager Request Rejected'),
            p('Your request to register as a store manager has been rejected'),
            p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def category_created(category_name:str):
    msg = html(
        head(
            h1('Category Request Created')
        ),
        body(
            h1('Category Created'),
            p('Your category request has been created successfully'),
            p('Your category name is: ', category_name),
            p('Please wait for approval'),
            p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def category_approved(category_name:str):
    msg = html(
        head(
            h1('Category Approved')
        ),
        body(
            h1('Category Request Approved'),
            p('Your category request has been approved successfully'),
            p('Your category name is: ', category_name),
            p('You can now add products to this category'),
            p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def category_rejected():
    msg = html(
        head(
            h1('Category Rejected')
        ),
        body(
            h1('Category Request Rejected'),
            p('Your category request has been rejected'),
            p('Thank you for using grocery store.')
        ),
    )
    return msg.render()





