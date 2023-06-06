import datetime


def date_before(days=30):
    return (datetime.datetime.utcnow() - datetime.timedelta(days=days)
            ).replace(microsecond=0).isoformat() + 'Z'


def date_now():
    return f'{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}Z'
