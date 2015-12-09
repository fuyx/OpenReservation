from google.appengine.api import mail
from datetime import time, datetime
from model import Reservation
from google.appengine.api.background_thread import background_thread

def getTime(hour, min):
    return time(int(hour), int(min))


def getDatetime(dt):
    return datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]))


def isEqual(s1, s2=''):
    if s1 == s2:
        return True
    else:
        return False


def deleteOutDateReservation():
    out_date_res = Reservation.query(Reservation.end_datetime < datetime.now())
    for reservation in out_date_res:
        reservation.key.delete()


def checkResourceTime(start, end, res_start, res_end):
    try:
        stime = time(int(start[3]), int(start[4]))
        etime = time(int(end[3]), int(end[4]))
    except:
        return False
    if (stime >= res_start and etime <= res_end):
        return True
    else:
        return False


def checkReservationConflict(resname,dt_start,dt_end):
    reservations=Reservation.query(Reservation.resource_name==resname).order(Reservation.start_datetime)
    prev_end_time=None
    last_reservation=None
    for reservation in reservations:
        if dt_end<=reservation.start_datetime:
            if prev_end_time is None or dt_start>=prev_end_time:
                return True
            else:
                return False
        last_reservation=reservation
    if last_reservation is None or dt_start>=last_reservation.end_datetime:
        return True
    return False

def genRSS(reservations,resource_name,dt):
    RSS='''
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<resource>
 <name>%s</name>
 <description>This is all the reservations of %s in RSS format</description>
 <lastBuildDate>%s</lastBuildDate>
 <pubDate>%s</pubDate>
 <ttl>1800</ttl>''' % (resource_name,resource_name,dt,dt)
    for reservation in reservations:
        RSS+='''
 <reservation>
  <user>%s</user>
  <starttime>%s</starttime>
  <endtime>%s</endttime>
 </reservation>''' % (reservation.user,reservation.start_datetime_string,reservation.end_datetime.strftime("%m/%d/%y,%H:%M:%S"))
    RSS+='''
</resource>
</rss>'''
    return RSS

def send_reserve_confirmation(address,reservation):
    mail.send_mail(sender="Open Reservation Team <easonfu1994@gmail.com>",
                   to=address,
                   subject='Reservation Auto Confirmation',
                   body='''
Dear %s:

You've already reserve %s from %s to %s :)

The Open Reservation Team
''' % (reservation.user,reservation.resource_name,reservation.start_datetime_string,reservation.end_datetime_string))


# def checkReservation():
#     reservations=Reservation.query(Reservation.start_datetime.strftime("%m/%d/%y,%H:%M")==datetime.now().strftime("%m/%d/%y,%H:%M"))
#     for reservation in reservations:
#         mail.send_mail(sender="Open Reservation Team",
#                        to=reservation.user,
#                        subject='Reservation Start Notification',
#                        body='''
# Dear %s:
#
# Your reservation of %s starts now!
#
# The Open Reservation Team
# ''' % (reservation.user,reservation.resource_name))
def checkReservation():
    reservations=Reservation.query(Reservation.start_datetime_string==datetime.now().strftime("%m/%d/%y,%H:%M"))
    for reservation in reservations:
        mail.send_mail(sender="Open Reservation Team",
                       to=reservation.user,
                       subject='Reservation Start Notification',
                       body='''
Dear %s:

Your reservation of %s starts now!

The Open Reservation Team
''' % (reservation.user,reservation.resource_name))
