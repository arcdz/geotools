import json
import math
from datetime import datetime
import random


#####################   Defs:   ###########################

# Define the input and output file paths
input_file  = '12905278.json'
output_file = '12905278.geojson'

def generate_random_hex_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

# Function to convert date-time string to timestamp
def convert_to_timestamp(date_str):
    # Parse the date-time string
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f%z")
    # Convert to timestamp
    return int(dt.timestamp())

# Function to calculate the angle between two vectors
def calculate_angle(vec1, vec2):
    dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
    mag1 = math.sqrt(vec1[0]**2 + vec1[1]**2)
    mag2 = math.sqrt(vec2[0]**2 + vec2[1]**2)
    cos_angle = dot_product / (mag1 * mag2)
    
    # corectii pentru erori de tipul cos = 1.00000000000002 
    if(cos_angle > 1): 
        cos_angle = 1
    if(cos_angle < -1):
        cos_angle = -1
        
    angle = math.acos(cos_angle)
    return math.degrees(angle)

# Function to identify turning points
def identify_turning_points(data, threshold=30):
    turning_points = []
    for i in range(1, len(data) - 1):
        lat1, lon1 = data[i-1]['latitudine'], data[i-1]['longitudine']
        lat2, lon2 = data[i]['latitudine'], data[i]['longitudine']
        lat3, lon3 = data[i+1]['latitudine'], data[i+1]['longitudine']
        
        vec1 = [lon2 - lon1, lat2 - lat1]
        vec2 = [lon3 - lon2, lat3 - lat2]
        angle = calculate_angle(vec1, vec2)
        
        if angle > threshold:
            turning_points.append(get_geo_turning_point(data[i],i, angle))
    return turning_points

# working
def create_line_segments(data, all_points_colors):
    line_string_segments = []
    for i in range(1, len(all_points_colors) ):
        id = all_points_colors[i][0] 
        prev_id = all_points_colors[i - 1][0] 
        color = all_points_colors[i - 1][1]  

        # print(f"i: {i}, i-1: {i - 1} Prev: {all_points_colors[i-1]}, curent: {all_points_colors[i]}")


        data_segment = [(
            point['longitudine'], 
            point['latitudine'],
            convert_to_timestamp(point['data_emitere']),
            point['data_emitere'],
            point['data_primire']) for point in data[prev_id:id+1]]
        
        line_string_segments.append(get_geo_line_string(data_segment, prev_id, color))
    return line_string_segments
        

#####################   construct:   ###########################

def get_geo_turning_point(data_point,index, angle):
     color = generate_random_hex_color()
     return {
                'type': 'Feature',
                'id' : index,
                'geometry': {
                    'type': 'Point',
                    'coordinates': [data_point['longitudine'], data_point['latitudine']]
                },
                'properties': {
                    'turning_angle': angle,
                    'timestamp': convert_to_timestamp(data_point['data_emitere']),
                    'data_emitere' : data_point['data_emitere'],
                    'data_primire' : data_point['data_primire'],
                    'marker-color': color,
                    'marker-size': 'small',
                    'marker-symbol': 'circle',
                    'dev-index' : index ,
                    'dev-color' : color
                }
            }

def get_geo_start_point(data_point,index):
     color = generate_random_hex_color()
     return {
                'type': 'Feature',
                'id' : index,
                'geometry': {
                    'type': 'Point',
                    'coordinates': [data_point['longitudine'], data_point['latitudine']]
                },
                'properties': {
                    'timestamp': convert_to_timestamp(data_point['data_emitere']),
                    'data_emitere' : data_point['data_emitere'],
                    'data_primire' : data_point['data_primire'],
                    'marker-color': color,
                    'marker-size': 'large',
                    'marker-symbol': 'entrance-alt1',
                    # 'dev-index' : index ,
                    # 'dev-color' : color
                }
            }
# Symbol:
# finish point = racetrack | gate
# start point = entrance-alt1 | arrow
def get_geo_special_point(data_point,index, symbol, name, description):
     color = generate_random_hex_color()
     return {
                'type': 'Feature',
                'id' : index,
                'geometry': {
                    'type': 'Point',
                    'coordinates': [data_point['longitudine'], data_point['latitudine']]
                },
                'properties': {
                    'timestamp': convert_to_timestamp(data_point['data_emitere']),
                    'data_emitere' : data_point['data_emitere'],
                    'data_primire' : data_point['data_primire'],
                    'marker-color': color,
                    'marker-size': 'large',
                    'marker-symbol': symbol,
                    # 'dev-index' : index ,
                    # 'dev-color' : color
                }
            }

def get_geo_line_string(data_segment, index,  color):
     return {
      "type": "Feature",
      "properties": {
        "stroke": color,
        "stroke-width": 5,
        "stroke-opacity": 1,
        # 'dev-index' : index ,
        # 'dev-color' : color
      },
      "geometry": {
        "type": "LineString",
        "coordinates": data_segment
      }
    }

#####################   Read:   ###########################
# Read the data from the input file
with open(input_file, 'r') as f:
    data = json.load(f)

# Sort the data by 'data_emitere'
data.sort(key=lambda x: x['data_emitere'])

# Identify turning points
turning_points = identify_turning_points(data)
start_point = get_geo_start_point(data[0],0)
finish_point = get_geo_start_point(data[-1],len(data))

all_points = [start_point] + turning_points + [finish_point]
all_points_colors = [(point['id'], point['properties']['marker-color']) for point in all_points]

line_strings = create_line_segments(data, all_points_colors)

#####################   Build GeoJSON:   ###########################

# Init GeoJSON
geojson = {
    "type": "FeatureCollection",
    "properties": { "Title":  "Avzi 1234556667",
                    ""
                    "vol":20},
    "features": line_strings + all_points
}

#####################   Write:   ###########################
# Write the output to the output file
with open(output_file, 'w') as f:
    json.dump(geojson, f, indent=2)

print("Conversion complete. Output written to", output_file)
