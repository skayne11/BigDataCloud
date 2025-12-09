from sgp4.api import Satrec, jday
import numpy as np

EARTH_RADIUS = 6371.0  # km

def tle_to_latlon(tle_line1, tle_line2):
    try:
        s = Satrec.twoline2rv(tle_line1, tle_line2)
        
        # obtenir le jour julien de l'époque du TLE
        year = s.epochyr
        if year < 57:
            year += 2000
        else:
            year += 1900
        jd, fr = jday(year, 1, 1, 0, 0, 0)
        jd_epoch = jd + (s.epochdays - 1)

        # propagation à t = 0 (l'époque du TLE)
        e, r, v = s.sgp4(0.0, 0.0)
        if e != 0:
            return None, None, None

        # r est en km dans le référentiel TEME, convertir en lat/lon
        x, y, z = r

        # latitude
        lat = np.degrees(np.arcsin(z / np.linalg.norm(r)))
        # longitude
        lon = np.degrees(np.arctan2(y, x))
        # altitude
        alt = np.linalg.norm(r) - EARTH_RADIUS

        return lat, lon, alt
    except Exception as ex:
        print("Erreur SGP4 :", ex)
        return None, None, None
