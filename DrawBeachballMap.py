from datetime import datetime
import os
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from obspy.imaging.beachball import beach
import sys
import numpy as np


import DrawGraphics


def convert_date_to_decimal(year, month, day, hour, minute): # Conversion of date to decimal form
  date_string = f'{year}-{month}-{day} {hour}:{minute}'
  date = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
  fractional_day = date.hour / 24 + date.minute / (24 * 60)
  return date.toordinal() + fractional_day


def optimal_width(area):
  if area <= 12:
    return 1e4
  elif area <= 44:
    return 3e4
  else:
    return 5e4  # Add value for large areas


if __name__ == '__main__':
  # lat_s = float(sys.argv[1])
  # lat_e = float(sys.argv[2])
  # lon_s = float(sys.argv[3])
  # lon_e = float(sys.argv[4])
  # h = float(sys.argv[5])
  lat_s = float(input("Enter the lower limit of the latitude: "))
  lat_e = float(input("Enter the upper limit of the latitude: "))
  lon_s = float(input("Enter the lower limit of the longitude: "))
  lon_e = float(input("Enter the upper limit of the longitude: "))
  h = float(input("Enter the step h with which you want to traverse the grid: "))

  area = (lat_e - lat_s) * (lon_e - lon_s)
  width = optimal_width(area)

  eq_name = os.path.join(os.getcwd (), 'DAILY_eqs.txt') # Open the DAILY_eqs.txt file for reading

  try:
    with open(eq_name, "r") as EQDATA:
      eq_data = EQDATA.readlines()
  except FileNotFoundError:
      print("Can't open", eq_name, "file with list of earthquakes.")
      exit()

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

        eq_dates.append("{:.4f}".format(convert_date_to_decimal(year, month, day, hour, minute)))
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

  m = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_e, llcrnrlon=lon_s, urcrnrlon=lon_e, resolution='h')

  for i in range(len(eq_dates)):
    x, y = m(eq_lons[i], eq_lats[i])
    b = beach([eq_strikes1[i], eq_dips1[i], eq_rakes1[i]], xy=(x, y), width=width, linewidth=0.5, facecolor='black')
    b.set_zorder(10)
    plt.gca().add_collection(b)

  folder_path = input('Enter the name of the directory containing the kmz files: ')
  folder_path = os.getcwd() + '/' + folder_path
  content = os.listdir(folder_path)
  content = [el for el in content if el != '.DS_Store']
  print(content)
  DrawGraphics.draw_faults(folder_path, content, m)  # Mapping of North Caucasus faults for 2018

  DrawGraphics.draw_regions(m)

  DrawGraphics.draw_stations(m)

  m.shadedrelief(scale=2.5, cmap='gist_earth')

  parallels = np.arange(lat_s, lat_e + 0.1, 1)  # Latitude in 1 degree increments
  meridians = np.arange(lon_s, lon_e + 0.1, 1)  # Longitude in 1 degree increments
  m.drawparallels(parallels, labels=[True, False, False, True], fontsize=10, color='grey', fmt='%i')
  m.drawmeridians(meridians, labels=[True, False, False, True], fontsize=10, color='grey', fmt='%i')

  plt.tight_layout()

  plt.savefig("beachballs.png", dpi=300)
