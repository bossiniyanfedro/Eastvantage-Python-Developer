import math

# earth radius in km
R_KM = 6371.0

def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance in km."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    a = max(0.0, min(1.0, a))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R_KM * c
