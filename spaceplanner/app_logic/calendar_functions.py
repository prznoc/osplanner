from datetime import datetime, timedelta

#Python 3.8 adds fromisocalendar()
def date_from_isoweek(iso_year, iso_weeknumber, iso_weekday):
    return datetime.strptime(
        '{:04d} {:02d} {:d}'.format(iso_year, iso_weeknumber, iso_weekday),
        '%G %V %u').date()
