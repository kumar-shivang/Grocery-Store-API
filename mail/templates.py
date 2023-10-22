import pyhtml as h


def manager_created(username: str):
    msg = h.html(
        h.head(
            h.h1('Manager Request Created')
        ),
        h.body(
            h.h1('Manager Request Created'),
            h.p('Your manager request has been created successfully'),
            h.p('Your username is: ', username),
            h.p('Please wait for approval'),
            h.p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def manager_approved(user_id: int, username: str):
    msg = h.html(
        h.head(
            h.h1('Manager Approved')
        ),
        h.body(
            h.h1('Manager Request Approved'),
            h.p('Your manager request has been approved successfully'),
            h.p('Your username is: ', username),
            h.p('Your user id is: ', user_id),
            h.p('You can now add products to the store'),
            h.p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def manager_rejected():
    msg = h.html(
        h.head(
            h.h1('Manager Rejected')
        ),
        h.body(
            h.h1('Manager Request Rejected'),
            h.p('Your manager request has been rejected'),
            h.p('Thank you for using grocery store.')
        ),
    )

    return msg.render()


def category_created(category_name: str):
    msg = h.html(
        h.head(
            h.h1('Category Request Created')
        ),
        h.body(
            h.h1('Category Request Created'),
            h.p('Your category request has been created successfully'),
            h.p('Your category name is: ', category_name),
            h.p('Please wait for approval'),
            h.p('Thank you for using grocery store.')
        ),
    )

    return msg.render()


def category_approved(category_name: str):
    msg = h.html(
        h.head(
            h.h1('Category Approved')
        ),
        h.body(
            h.h1('Category Request Approved'),
            h.p('Your category request has been approved successfully'),
            h.p('Your category name is: ', category_name),
            h.p('You can now add products to the store'),
            h.p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


def category_rejected():
    msg = h.html(
        h.head(
            h.h1('Category Rejected')
        ),
        h.body(
            h.h1('Category Request Rejected'),
            h.p('Your category request has been rejected'),
            h.p('Thank you for using grocery store.')
        ),
    )

    return msg.render()
