import time
import random

measured_time = []

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        # print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))
        measured_time.append({'type': f.__name__, 'time': (time2-time1)*1000.0})
        return ret
    return wrap

def odds_are(prob):
    rand = random.uniform(0, 1)
    return prob <= rand
