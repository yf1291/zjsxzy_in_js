import datetime

def days_delta(date1, date2):
    days = (datetime.datetime.strptime(date1, '%Y-%m-%d') - datetime.datetime.strptime(date2, '%Y-%m-%d')).days
    return days