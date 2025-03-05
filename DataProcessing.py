import zipfile
import xml.etree.ElementTree as ET
import re
import numpy as np
import os
import MathPart


def open_kmz(folder_path, filename):
  # Opens the kmz file and extracts the KML content
  with zipfile.ZipFile(folder_path + '/' + filename, 'r') as kmz_file:
    # Get a list of the files in the archive
    files = kmz_file.namelist()
    # Find the KML file
    kml_file = [f for f in files if f.endswith('.kml')][0]
    # Extract the KML file
    with kmz_file.open(kml_file) as kml_data:
      kml_content = kml_data.read().decode('utf-8')
      return kml_content


def extract_coordinates(kml_content):
  # KML parsing
  root = ET.fromstring(kml_content)

  # Creating a list for storing coordinates
  all_coordinates, conf, rate = [], [], []

  # Iterate through all Placemark
  for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
    # Getting coordinates from LineString
    coordinates_string = placemark.find('.//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates').text
    # Separation of coordinates by spaces
    coordinates = coordinates_string.split()
    # Преобразование координат в float и группировка в пары
    coordinates = [[float(coord.split(',')[0]), float(coord.split(',')[1])] for coord in coordinates]
    # Converting coordinates to float and grouping into pairs
    all_coordinates.append(coordinates)

    description = placemark.find('.//{http://www.opengis.net/kml/2.2}description').text
    # Extracting fault information from the fault description
    match = re.search(r'CONF=\s+<b>(.?)</b>', description)
    if match:
      conf_value = match.group(1)
      # Creating a list for storing fault data
      fault_data = [conf_value]
      # Adding fault data to the list of all data
      conf.append(fault_data)

    match = re.search(r'RATE=\s+<b>(.?)</b>', description)
    if match:
      rate_value = match.group(1)
      # Creating a list for storing fault data
      fault_data = [rate_value]
      # Adding fault data to the list of all data
      rate.append(fault_data)

  return all_coordinates, conf, rate


def get_offsets():
  eq_name = os.path.join(os.getcwd(), 'results.txt')
  try:
    with open(eq_name, "r") as EQDATA:
      eq_data = EQDATA.readlines()
  except FileNotFoundError:
    print("Can't open", eq_name, "file with list of earthquakes.")
    exit()

  lat, lon, ux_1, uy_1, uz_1, ux_2, uy_2, uz_2 = [], [], [], [], [], [], [], []
  count = 0
  k = 0
  for i, line in enumerate(eq_data):
    line = line.strip()

    if count == 0 or count == 1:
      line_split = line[7:-1].split(',')
    else:
      line_split = line[8:-1].split(',')

    for j in range(len(line_split)):
      line_split[j] = line_split[j].strip(" ")
    for j in range(len(line_split)):
      line_split[j] = line_split[j].strip("''")

    if count == 0:
      lat.append(line_split)
      count += 1
    elif count == 1:
      lon.append(line_split)
      count += 1
    elif count == 2:
      ux_1.append(line_split)
      count += 1
    elif count == 3:
      uy_1.append(line_split)
      count += 1
    elif count == 4:
      uz_1.append(line_split)
      count += 1
    elif count == 5:
      ux_2.append(line_split)
      count += 1
    elif count == 6:
      uy_2.append(line_split)
      count += 1
    elif count == 7:
      uz_2.append(line_split)
      k += 1
      count = 0
  del k

  index1, index2 = np.zeros(len(ux_1[0])), np.zeros(len(ux_2[0]))
  array1, max_ux1, max_uy1 = np.zeros(len(ux_1[0])), np.zeros(len(ux_1[0])), np.zeros(len(uy_1[0]))
  array2, max_ux2, max_uy2 = np.zeros(len(ux_2[0])), np.zeros(len(ux_2[0])), np.zeros(len(uy_2[0]))

  for j in range(len(array1)):
    array1[j] = -1e99
    array2[j] = -1e99

  for j in range(len(ux_1)):
    for k in range(len(ux_1[j])):
      if MathPart.len_vector(float(ux_1[j][k]), float(uy_1[j][k])) >= array1[k]:
        index1[k] = j
        array1[k] = MathPart.len_vector(float(ux_1[j][k]), float(uy_1[j][k]))
        max_ux1[k] = float(ux_1[j][k])
        max_uy1[k] = float(uy_1[j][k])
      if MathPart.len_vector(float(ux_2[j][k]), float(uy_2[j][k])) >= array2[k]:
        index2[k] = j
        array2[k] = MathPart.len_vector(float(ux_2[j][k]), float(uy_2[j][k]))
        max_ux2[k] = float(ux_2[j][k])
        max_uy2[k] = float(uy_2[j][k])

  return lat[0], lon[0], max_ux1, max_uy1, array1, max_ux2, max_uy2, array2, index1, index2
