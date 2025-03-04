from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import pandas as pd
from obspy.imaging.beachball import beach
import os
from datetime import datetime
import numpy as np
import sys


def convert_date_to_decimal(year, month, day, hour, minute):
  date_string = f'{year}-{month}-{day} {hour}:{minute}'
  date = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
  fractional_day = date.hour / 24 + date.minute / (24 * 60)
  return date.toordinal() + fractional_day


def convert_decimal_to_date(decimal_date):
  decimal_date = float(decimal_date)
  date_ordinal = int(decimal_date)
  fractional_day = decimal_date - date_ordinal
  date = datetime.fromordinal(date_ordinal)
  hour = int(fractional_day * 24)
  minute = int((fractional_day * 24 * 60) % 60)
  return date.year, date.month, date.day, hour, minute


def get_quakes():
  eq_name = os.path.join(os.getcwd(), 'DAILY_eqs.txt')

  try:
    with open(eq_name, "r") as EQDATA:
      eq_data = EQDATA.readlines()
  except FileNotFoundError:
    print("Can't open", eq_name, "file with list of earthquakes.")
    exit()

  eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2 = [], [], [], [], [], [], [], [], [], [], [], []
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
  return eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2


def draw_map(lat_s, lat_e, lon_s, lon_e, lat, lon, ux_1, uy_1, uz_1, ux_2, uy_2, uz_2, eq_dates, eq_lats, eq_lons, eq_depths,
             eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2):
  plt.clf()
  year, month, day, hour, minute = convert_decimal_to_date(eq_dates)
  plt.text(0.5, 1.05, s=f'{year}/{month}/{day}: lat = {eq_lats}, lon = {eq_lons}, depth = {eq_depths}, Mw = {eq_mags}',
           horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
  eqs = pd.DataFrame({
    'latitude': [eq_lats],
    'longitude': [eq_lons],
    'depth': [eq_depths],
    'magnitude': [eq_mags],
    'strike': [eq_strikes1],
    'dip': [eq_dips1],
    'rake': [eq_rakes1]
  })

  m = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_e, llcrnrlon=lon_s, urcrnrlon=lon_e, resolution='h')
  m.shadedrelief()

  for index, row in eqs.iterrows():
      x, y = m(row['longitude'], row['latitude'])
      b = beach([row['strike'], row['dip'], row['rake']], xy=(x, y), width=7e4, linewidth=2, facecolor='black')
      b.set_zorder(10)
      plt.gca().add_collection(b)

  print(f'ux_1 {ux_1}')
  for i in range(len(lat)):
      x, y = m(float(lon[i]), float(lat[i]))
      plt.annotate("", xy=(x + float(ux_1[i])*10e6, y + float(uy_1[i])*10e6), xytext=(x, y),
                   arrowprops=dict(arrowstyle="->", color='black', linewidth=0.5))

  plt.savefig(str(year) + "_" + str(month) + "_" + str(day) + "_" + str(eq_lats) + "_" + str(eq_lons) + ".png", dpi=300)
  # plt.show()


def len_vector(x, y):
  return np.sqrt(x**2 + y**2)


def get_offsets(eqt_s, lat_e, lon_s, lon_e, eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2):
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

  array1, max_ux1, max_uy1 = np.zeros(len(ux_1[0])), np.zeros(len(ux_1[0])), np.zeros(len(uy_1[0]))
  array2, max_ux2, max_uy2 = np.zeros(len(ux_2[0])), np.zeros(len(ux_2[0])), np.zeros(len(uy_2[0]))
  for j in range(len(ux_1)):
    for i in range(len(ux_1[j])):
      if len_vector(float(ux_1[j][i]), float(uy_1[j][i])) >= array1[i]:
        array1[i] = len_vector(float(ux_1[j][i]), float(uy_1[j][i]))
        max_ux1[i] = float(ux_1[j][i])
        max_uy1[i] = float(uy_1[j][i])
      if len_vector(float(ux_2[j][i]), float(uy_2[j][i])) >= array2[i]:
        array2[i] = len_vector(float(ux_2[j][i]), float(uy_2[j][i]))
        max_ux2[i] = float(ux_2[j][i])
        max_uy2[i] = float(uy_2[j][i])
      # draw_map(at_s, lat_e, lon_s, lon_e, lat[i], lon[i], ux_1[i], uy_1[i], uz_1[i], ux_2[i], uy_2[i], uz_2[i], eq_dates[i], eq_lats[i], eq_lons[i], eq_depths[i], eq_mags[i], eq_moments[i], eq_strikes1[i], eq_dips1[i], eq_rakes1[i], eq_strikes2[i], eq_dips2[i], eq_rakes2[i])
  return lat[0], lon[0], max_ux1, max_uy1, array1, max_ux2, max_uy2, array2


def draw_displacement_map(arr, lat_s, lat_e, lon_s, lon_e, h):
  m = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_e, llcrnrlon=lon_s, urcrnrlon=lon_e, resolution='h')
  plt.clf()

  lat = np.arange(lat_s, lat_e + 0.01, h)
  lon = np.arange(lon_s, lon_e + 0.01, h)

  displacements_data = np.zeros((len(lat), len(lon)))
  k = 0
  for i in range(len(displacements_data)):
    for j in range(len(displacements_data[i])):
      displacements_data[i][j] = arr[k]
      k += 1
  # displacements_data = arr.reshape((len(lat), len(lon)))

  lons, lats = np.meshgrid(lon, lat)
  x, y = m(lons, lats)

  # Draw displacement isolines
  plt.contourf(x, y, displacements_data, cmap='jet', alpha=0.4)  # Display the displacement data as a colored surface
  plt.colorbar()  # Add a color bar

  m.shadedrelief(scale=2.5, cmap='gist_earth')

  # Add a coordinate grid
  parallels = np.arange(lat_s, lat_e + 0.01, 1)  # Latitude in 1 degree increments
  meridians = np.arange(lon_s, lon_e + 0.01, 1)  # Longitude in 1 degree increments
  m.drawparallels(parallels, labels=[True, False, False, True], fontsize=10, color='grey')
  m.drawmeridians(meridians, labels=[True, False, False, True], fontsize=10, color='grey')

  plt.tight_layout()

  plt.title('Карта смещений')
  plt.savefig("displacement_map.png", dpi=300)


if __name__ == '__main__':
  lat_s = float(sys.argv[1])
  lat_e = float(sys.argv[2])
  lon_s = float(sys.argv[3])
  lon_e = float(sys.argv[4])
  h = float(sys.argv[5])
  eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2 = get_quakes()

  # for i in range(len(eq_dates)):
  #   year, month, day, hour, minute = convert_decimal_to_date(eq_dates[i])
  #   print(f'{year}/{month}/{day}: lat = {eq_lats[i]}, lon = {eq_lons[i]}, depth = {eq_depths[i]}, Mw = {eq_mags[i]}, scalar_moment = {eq_moments[i]}, '
  #         f'strike1 = {eq_strikes1[i]}, dip1 = {eq_dips1[i]}, rake1 = {eq_rakes1[i]}, '
  #         f'strike2 = {eq_strikes2[i]}, dip2 = {eq_dips2[i]}, rake2 = {eq_rakes2[i]}')

  lats, lons, ux_1, uy_1, arr_1, ux_2, uy_2, arr_2 = get_offsets(lat_s, lat_e, lon_s, lon_e, eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2)
  arr_res = np.zeros(len(ux_1))
  for i in range(len(arr_1)):
    if arr_1[i] >= arr_2[i]:
      arr_res[i] = arr_1[i]
    elif arr_1[i] <= arr_2[i]:
      arr_res[i] = arr_2[i]
  # print(arr_res)
  draw_displacement_map(arr_res, lat_s, lat_e, lon_s, lon_e, h)

  file = open("surface_displacement.txt", "w")
  line1 = 'lat, lon, ux_1, uy_1, sqrt(ux_1**2 + uy_1**2), ux_2, uy_2, sqrt(ux_2**2 + uy_2**2)\n'
  line2 = '{}\n'.format(lats)
  line3 = '{}\n'.format(lons)
  line4 = '{}\n'.format(ux_1)
  line5 = '{}\n'.format(uy_1)
  line6 = '{}\n'.format(arr_1)
  line7 = '{}\n'.format(ux_2)
  line8 = '{}\n'.format(uy_2)
  line9 = '{}\n'.format(arr_2)
  file.write(line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9)
  file.close()

