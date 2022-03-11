# -*- coding: utf-8 -*-
"""Setup the cattle-monitor application"""
from __future__ import print_function, unicode_literals
import transaction
from cattle_monitor import model
from cattle_monitor.model import DBSession


def bootstrap(command, conf, vars):
    """Place any commands to setup cattle_monitor here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        users = [
            ('tafadzwa@gmail.com', 'Tafadzwa Mutero', '12345678', ['administrator', 'super_admin']),

        ]
        for user_name, display_name, password, roles in users:
            u = model.DBSession.query(model.User). \
                filter(model.User.user_name == user_name). \
                filter(model.User.display_name == display_name). \
                filter(model.User.email_address == user_name). \
                first()

            if not u:
                u = model.User()
                u.user_name = user_name
                u.display_name = display_name
                u.email_address = user_name
                if password:
                    u.password = password

                model.DBSession.add(u)
                model.DBSession.flush()

            for role in roles:
                r = model.DBSession.query(model.Role). \
                    filter(model.Role.name == role). \
                    first()
                if not r:
                    r = model.Role()
                    r.name = role
                    r.description = f"{role.replace('_', ' ').title()}s Role"

                r.users.append(u)
                model.DBSession.add(r)
                model.DBSession.flush()

        transaction.commit()

    except IntegrityError:
        print('Warning, there was a problem adding your auth data, '
              'it may have already been added:')
        import traceback
        print(traceback.format_exc())
        transaction.abort()
        print('Continuing with bootstrapping...')

    # <websetup.bootstrap.after.auth>
