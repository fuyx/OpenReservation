from datetime import time, datetime

from model import Reservation


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
        reservation.delete()


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


def checkReservationConflict(dt_start,dt_end):
    reservations=Reservation.query().order(Reservation.start_datetime)
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
