from pyhtml import *


def managerCreated(username:str):
    msg = html(
        head(
            title('Manager Created')
        ),
        body(
            h1('Manager Request Created'),
            p('Your request has been created successfully, wait for approval'),
            p('Your username is: ', username),
            p('Thank you for using grocery store.')
        ),
    )
    return msg.render()


