# parse_tle.py (robuste)
import re
from sgp4.api import Satrec, jday
from datetime import datetime, timedelta, timezone
import numpy as np
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("parse_tle")

MU_EARTH = 398600.4418  # km^3 / s^2
EARTH_RADIUS_KM = 6371.0

def classify_type(name):
    n = name.upper()
    if "ISS" in n:
        return "Station spatiale"
    if "HUBBLE" in n:
        return "Télescope"
    if "GPS" in n or "NAVSTAR" in n:
        return "Navigation"
    if "WEATHER" in n or "METEOR" in n or "MET-" in n:
        return "Météo"
    if "STARLINK" in n or "ONEWEB" in n or "KU" in n:
        return "Internet / Telecom"
    return "Inconnu"

def mean_motion_to_altitude(mean_motion_rev_per_day):
    """
    Approximate semi-major axis from mean motion (n rev/day) using Kepler:
    n (rad/s) = sqrt(mu / a^3)  -> a = (mu / n^2)^(1/3)
    mean_motion_rev_per_day -> rad/s
    Returns altitude in km (semi-major axis - Earth radius)
    """
    try:
        n_rev_per_s = mean_motion_rev_per_day / 86400.0
        n_rad_s = n_rev_per_s * 2 * math.pi
        a_km = (MU_EARTH / (n_rad_s**2)) ** (1.0 / 3.0)
        alt_km = a_km - EARTH_RADIUS_KM
        return float(alt_km)
    except Exception:
        return None

def safe_epoch_datetime(epoch_year_short, epoch_day):
    """
    Convertit epochyr (2-digit) et epochdays (day-of-year.fraction) en datetime UTC.
    """
    try:
        yr = int(epoch_year_short)
        if yr < 57:
            yr += 2000
        else:
            yr += 1900
        # day_of_year -> datetime
        day_int = int(math.floor(epoch_day))
        frac_day = epoch_day - day_int
        epoch = datetime(yr, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_int - 1) + timedelta(seconds=frac_day * 86400.0)
        return epoch
    except Exception as e:
        logger.debug("safe_epoch_datetime error: %s", e)
        return None

def parse_tle_text(tle_text, clamp_future_days=1.0):
    """
    Retourne une liste de dict pour chaque TLE.
    clamp_future_days: si epoch est dans le futur de plus de cette valeur (jours),
                      on forcera la propagation à epoch (tsince=0) au lieu de propager dans le futur.
    """
    lines = [l.rstrip() for l in tle_text.splitlines() if l.strip()]
    sats = []

    for i in range(0, len(lines), 3):
        try:
            name = lines[i]
            line1 = lines[i+1]
            line2 = lines[i+2]
        except IndexError:
            break

        doc = {
            "name": name,
            "line1": line1,
            "line2": line2,
            "catalog_number": None,
            "approx_alt_km": None,
            "orbit_class": "UNKNOWN",
            "type": classify_type(name)
        }

        # catalog number
        try:
            doc["catalog_number"] = int(line1[2:7].strip())
        except Exception:
            pass

        # parse mean motion from line2 for fallback (cols 53-63 in 1-based, index 52:63)
        mean_motion = None
        try:
            mm_str = line2[52:63].strip()
            if mm_str:
                mean_motion = float(mm_str)  # revs per day
        except Exception:
            mean_motion = None

        # compute epoch datetime
        epoch_dt = None
        try:
            # use sgp4 parsed values if possible
            s = Satrec.twoline2rv(line1, line2)
            epoch_dt = safe_epoch_datetime(s.epochyr, s.epochdays)
        except Exception as e:
            logger.debug("SGP4 twoline2rv failed for %s: %s", name, e)
            epoch_dt = None

        # compute tsince (minutes) relative to epoch -> now
        tsince_min = 0.0
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        if epoch_dt:
            delta = now - epoch_dt
            delta_days = delta.total_seconds() / 86400.0
            # if epoch in future - clamp behaviour:
            if delta_days < 0:
                # epoch is in the future
                if abs(delta_days) <= clamp_future_days:
                    # small future offset: use tsince = 0 (propagate at epoch)
                    tsince_min = 0.0
                else:
                    # too far in future: treat as epoch (safe)
                    tsince_min = 0.0
            else:
                tsince_min = delta.total_seconds() / 60.0
        else:
            tsince_min = 0.0

        # First attempt: use sgp4 propagation at tsince_min
        used_sgp4 = False
        try:
            # s may be created above; if not, create it now
            if 's' not in locals():
                s = Satrec.twoline2rv(line1, line2)
            # sgp4 expects minutes since epoch
            e_code, r, v = s.sgp4(tsince_min, 0.0)
            if e_code == 0:
                used_sgp4 = True
                dist_km = float(np.linalg.norm(r))
                approx_alt = dist_km - EARTH_RADIUS_KM
                # sanity filter: plausible altitudes between 80 km and 100000 km
                if approx_alt is None or approx_alt < 80 or approx_alt > 100000:
                    # mark as invalid, fallback next
                    approx_alt = None
                doc["approx_alt_km"] = approx_alt
        except Exception as e:
            logger.debug("sgp4 propagation failed for %s: %s", name, e)
            doc["approx_alt_km"] = None

        # Fallback: if sgp4 failed or returned invalid altitude, try mean-motion -> altitude
        if doc["approx_alt_km"] is None and mean_motion is not None:
            try:
                alt_from_mm = mean_motion_to_altitude(mean_motion)
                # sanity check same bounds
                if alt_from_mm is not None and 80 <= alt_from_mm <= 100000:
                    doc["approx_alt_km"] = alt_from_mm
            except Exception as e:
                logger.debug("mean motion fallback failed for %s: %s", name, e)

        # Final classification of orbit_class
        alt = doc["approx_alt_km"]
        if alt is None:
            doc["orbit_class"] = "UNKNOWN"
        else:
            if alt < 2000:
                doc["orbit_class"] = "LEO"
            elif alt < 35786 - 200:
                doc["orbit_class"] = "MEO"
            elif abs(alt - 35786) <= 200:
                doc["orbit_class"] = "GEO"
            else:
                doc["orbit_class"] = "HEO"

        sats.append(doc)

    return sats

# test rapide si run direct
if __name__ == "__main__":
    from fetch_tle import fetch_tle
    txt = fetch_tle()
    docs = parse_tle_text(txt)
    print(f"Parsed {len(docs)} sats, exemples:")
    for d in docs[:10]:
        print(d["name"], d["approx_alt_km"], d["orbit_class"], d["type"])
