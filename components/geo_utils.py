import math

# Default coordinates: Currently set to central coordinates (can be edited by Admin/Developer later)
# Using a generic coordinate for Pune as a placeholder
COLLEGE_LATITUDE = 18.5204   
COLLEGE_LONGITUDE = 73.8567  
MAX_ALLOWED_RADIUS_METERS = 500.0

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters.
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371000 # Radius of earth in meters
    return c * r

def is_within_campus(student_lat, student_lon):
    """
    Check if the student's GPS coordinate is within the allowed campus radius.
    """
    distance = calculate_haversine_distance(
        COLLEGE_LATITUDE, COLLEGE_LONGITUDE,
        student_lat, student_lon
    )
    return distance <= MAX_ALLOWED_RADIUS_METERS, distance
