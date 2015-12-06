from datetime import *

from model import Reservation


def getTime(hour,min):
    return time(int(hour),int(min))
def getDatetime(dt):
    return datetime(int(dt[0]),int(dt[1]),int(dt[2]),int(dt[3]),int(dt[4]))
def isEqual(s1,s2=''):
    if s1 == s2:
        return True
    else:
        return False

def deleteOutDateReservation():
    out_date_res = Reservation.query(Reservation.end_datetime < datetime.now())
    for reservation in out_date_res:
        reservation.delete()