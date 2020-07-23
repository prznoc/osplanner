from datetime import datetime, timedelta

#Python 3.8 adds fromisocalendar() to replace this
def date_from_isoweek(iso_year, iso_weeknumber, iso_weekday):
    iso_weekday = iso_weekday + 1 #code below assumes that monday is 1, add is required to keep monday as 0
    return datetime.strptime(
        '{:04d} {:02d} {:d}'.format(iso_year, iso_weeknumber, iso_weekday),
        '%G %V %u').date()
