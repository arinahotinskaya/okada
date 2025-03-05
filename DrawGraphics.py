import csv
import matplotlib.pyplot as plt
from obspy.imaging.beachball import beach
import numpy as np
import os


import DataProcessing
import MathPart


def draw_catalog_quakes_old(beachball_lon, beachball_lat, beachball_dates, m):
  # Building a catalogue of earthquakes (from -550 to the present day)
  with open('export.csv', newline='') as f:
    reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_NONE)
    data = []
    for row in reader:
      for j, item in enumerate(row):
        row[j] = item.replace(',', '.')
      data.append(row)

    for j, row in enumerate(data):
      print(f'{j + 1}: {row}')
      if j > 0:

        year = int(row[0])
        month = int(row[1])
        day = int(row[2])
        hour = int(row[3])
        minute = int(row[4])

        latitude = float(row[6])
        longitude = float(row[7])
        depth = float(row[8])
        magnitude = float(row[9])

        size = 0
        color = 'black'

        # Depth sorting
        if depth > 20:
          color = 'dimgray'
        if depth >= 40:
          color = 'silver'

        # Magnitude sorting
        if 9 <= magnitude <= 10:
          size = 5
        elif 7 <= magnitude < 9:
          size = 3
        elif magnitude < 7:
          size = 1

        flag = False
        for k in range(len(beachball_lat)):
          yearCMT, monthCMT, dayCMT, hourCMT, minuteCMT = MathPart.convert_decimal_to_date(beachball_dates[k])

          if (year == yearCMT and month == monthCMT and day == dayCMT and hour == hourCMT and
            (minuteCMT - 5 <= minute <= minuteCMT + 5) and (beachball_lat[k] - 0.1 <= latitude <= beachball_lat[k] + 0.1) and
            (beachball_lon[k] - 0.1 <= longitude <= beachball_lon[k] + 0.1)):
            flag = True
            # print(
            #   f'\nTHERE IS A MATCH!\n{yearCMT}/{monthCMT}/{dayCMT}/{hourCMT}/{minuteCMT}\n'
            #   f'{year}/{month}/{day}/{hour}/{minute}\nlat = {latitude} lon = {longitude}\n'
            #   f'latGlobalCMT = {beachball_lat[k]} lonGlobalCMT = {beachball_lon[k]}\n')

        if not flag:
          x, y = m(longitude, latitude)
          # ДОБАВОЧКА
          color = 'black'
          size = 2
          plt.plot(x, y, 'ro', markersize=size, color=color)


# def draw_catalog_quaqes(area, index, m):
def draw_catalog_quaqes(area, m):
  with open('DAILY_eqs.txt', "r") as EQDATA:
    eq_data = EQDATA.readlines()
    eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2 = [], [], [], [], [], [], [], [], [], [], [], []
    hour, minute = "", ""
    for i, line in enumerate(eq_data):
      if i >= 2:
        line = line.strip()
        line_split = line.split(' ')
        line_split = [i for i in line_split if i]
        line_split = line_split[:15]

        if len(line_split) == 15:
          year = line_split[0]
          month = line_split[1]
          day = line_split[2]
          time = line_split[3]
          lat = line_split[4]
          lon = line_split[5]
          depth = line_split[6]
          magnitude = line_split[7]
          moment = line_split[8]
          strike1 = line_split[9]
          dip1 = line_split[10]
          rake1 = line_split[11]
          strike2 = line_split[12]
          dip2 = line_split[13]
          rake2 = line_split[14]

          hour = time[:2]
          format_flag = 0
          if hour[1] == ':':
            hour = '0' + hour[0]
            format_flag = 1
          if format_flag == 0:
            minute = time[3:5]
          else:
            minute = time[2:4]
          if minute[1] == ':':
            minute = '0' + minute[0]

          eq_dates.append("{:.4f}".format(MathPart.convert_date_to_decimal(year, month, day, hour, minute)))
          eq_lats.append(float(lat))
          eq_lons.append(float(lon))
          eq_depths.append(float(depth))
          eq_mags.append(float(magnitude))
          eq_moments.append(float(moment))
          eq_strikes1.append(float(strike1))
          eq_dips1.append(float(dip1))
          eq_rakes1.append(float(rake1))
          eq_strikes2.append(float(strike2))
          eq_dips2.append(float(dip2))
          eq_rakes2.append(float(rake2))

          # PRINT TITLE
          # year, month, day, _, _ = MathPart.convert_decimal_to_date(eq_dates[0])
          # plt.title(f'{year}/{month}/{day}: strike = {eq_strikes2[0]}, dip = {eq_dips2[0]}, rake = {eq_rakes2[0]}')

    for i in range(len(eq_dates)):
    # for i in index:
      i = int(i)
      # print(i)
      # print(type(i))
      x, y = m(eq_lons[i], eq_lats[i])
      width = MathPart.optimal_width(area, eq_mags[i])
      b = beach([eq_strikes1[i], eq_dips1[i], eq_rakes1[i]], xy=(x, y), width=width, linewidth=0.5, facecolor='black')
      b.set_zorder(10)
      plt.gca().add_collection(b)

    return eq_lons, eq_lats, eq_dates


def draw_faults(folder_path, content, m):
  n = len(content)

  # Building a fault map
  for i in range(n):
    file_name = content[i]
    kml_content = DataProcessing.open_kmz(folder_path, file_name)
    # print(kml_content)

    coordinates_list, conf_list, rate_list = DataProcessing.extract_coordinates(kml_content)
    # Output of coordinates for each fault
    # for j, coordinates in enumerate(coordinates_list):
    #   print(f"Разлом {j + 1}: {coordinates}")

    colors = ['darkred', 'red', 'orange', 'grey']
    linewidths = [1.5, 1, 0.5]
    for j, coordinates in enumerate(coordinates_list):
      color, linewidth = '', 0
      # Converting coordinates to a map projection
      x, y = m([coord[0] for coord in coordinates], [coord[1] for coord in coordinates])

      if rate_list[j][0] == '1' and conf_list[j][0] == 'A':
        color = colors[0]
        linewidth = linewidths[0]
      elif rate_list[j][0] == '2' and conf_list[j][0] == 'A':
        color = colors[0]
        linewidth = linewidths[1]
      elif rate_list[j][0] == '3' and conf_list[j][0] == 'A':
        color = colors[0]
        linewidth = linewidths[2]
      elif rate_list[j][0] == '1' and conf_list[j][0] == 'B':
        color = colors[1]
        linewidth = linewidths[0]
      elif rate_list[j][0] == '2' and conf_list[j][0] == 'B':
        color = colors[1]
        linewidth = linewidths[1]
      elif rate_list[j][0] == '3' and conf_list[j][0] == 'B':
        color = colors[1]
        linewidth = linewidths[2]
      elif rate_list[j][0] == '2' and conf_list[j][0] == 'C':
        color = colors[2]
        linewidth = linewidths[1]
      elif rate_list[j][0] == '3' and conf_list[j][0] == 'C':
        color = colors[2]
        linewidth = linewidths[2]
      elif rate_list[j][0] == '3' and conf_list[j][0] == 'D':
        color = colors[3]
        linewidth = linewidths[2]

      # Drawing a line
      plt.plot(x, y, color=color, linewidth=linewidth)


def draw_displacement_map(arr, lat_s, lat_e, lon_s, lon_e, h, m):
  plt.clf()
  lat = np.arange(lat_s, lat_e + 0.01, h) # Create coordinate grid
  lon = np.arange(lon_s, lon_e + 0.01, h)

  displacements_data = np.zeros((len(lat), len(lon)))
  k = 0
  for i in range(len(displacements_data)):
    for j in range(len(displacements_data[i])):
      displacements_data[i][j] = arr[k]
      k += 1
  # displacements_data = arr.reshape((len(lat), len(lon)))

  lons, lats = np.meshgrid(lon, lat) # Project the coordinates onto the map plane
  x, y = m(lons, lats)


  # min_val = 0.5
  # max_val = np.max(displacements_data)
  # # Создайте список меток с шагом 0.25
  # ticks = np.arange(min_val, max_val + 2.5, 2.5)

  min_val = 0.5
  max_val = np.max(displacements_data)
  # Создайте список меток с шагом 0.25
  ticks = np.arange(min_val, max_val + 2.5, 2.5)

  # plt.contourf(x, y, displacements_data, cmap='jet', alpha=0.4)
  # plt.colorbar()
  plt.contourf(x, y, displacements_data, levels=ticks, cmap='jet', alpha=0.4)  # Draw displacement isolines
  plt.colorbar(ticks=ticks)

  # plt.colorbar()  # Add colour scale

  # plt.xlabel('Longitude')
  # plt.ylabel('Latitude')
  # plt.title('Карта смещений и разломов')


def draw_regions(m):
  folder_path = input('Enter the name of the directory containing regions: ')
  folder_path = os.getcwd() + '/' + folder_path
  content = os.listdir(folder_path)
  content = [el for el in content if el != '.DS_Store']
  print(content)

  for i in range(len(content)):
    lons, lats = [], []

    eq_name = folder_path + '/' + content[i]

    try:
      with open(eq_name, "r") as EQDATA:
        eq_data = EQDATA.readlines()
    except FileNotFoundError:
      print("Can't open", eq_name, "file with list of earthquakes.")
      exit()

    for j, line in enumerate(eq_data):
      line = line.strip().split(" ")
      line = [item for item in line if item]

      lons.append(line[0])
      lats.append(line[1])
      # print(line)

    lons = [float(item) for item in lons if item]
    lats = [float(item) for item in lats if item]
    x, y = m(lons, lats)
    # x = x + [x[0]]
    # y = y + [y[0]]

    plt.plot(x, y, '-', color = 'black', linewidth=0.75)


def draw_stations(m):
  name_of_station_1 = ['ARNR', 'BTKR', 'VLKR', 'DIGR', 'KMGR', 'KORR', 'LACR', 'LSNR', 'PRTR', 'STDR', 'TRKR', 'MRMR', 'PXTR', 'ZEI']
  lon_1 = [44.29, 44.54, 44.68, 43.57, 44.87, 44.07, 44.30, 43.80, 44.28, 44.06, 44.73, 44.48, 44.62, 43.90]
  lat_1 = [43.18, 43.37, 43.05, 42.89, 43.06, 43.09, 42.83, 43.27, 43.75, 43.37, 43.72, 43.01, 42.97, 42.79]

  for i in range(len(name_of_station_1)):
    x, y = m(lon_1[i], lat_1[i])
    plt.plot(x, y, '^', markersize=4.9, color='blue')
    # plt.text(x + 0.1, y + 0.1, name_of_station[i], fontsize=8, color='blue')

  name_of_station_2 = ['VLKZ', 'LATZ', 'PRTN', 'ARDN', 'KAMT']
  lon_2 = [44.68, 44.3, 44.28, 44.28, 43.78]
  lat_2 = [43.05, 42.83, 43.75, 43.17, 42.95]

  for i in range(len(name_of_station_2)):
    x, y = m(lon_2[i], lat_2[i])
    plt.plot(x, y, '^', markersize=4.9, color='red')
