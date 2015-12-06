from datetime import *
def getTime(hour,min):
    return time(int(hour),int(min))
def getDatetime(dt):
    return datetime(int(dt[0]),int(dt[1]),int(dt[2]),int(dt[3]),int(dt[4]))