import math
from datetime import datetime
import os
import subprocess
import numpy as np


def convert_date_to_decimal(year, month, day, hour, minute):
  date_string = f'{year}-{month}-{day} {hour}:{minute}'
  date = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
  fractional_day = date.hour / 24 + date.minute / (24 * 60)
  return date.toordinal() + fractional_day


def quakes():
  eq_name = os.path.join(os.getcwd (), 'DAILY_eqs.txt')
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
          minu:wte = time[2:4]
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


def run_program(point_lat, point_lon, eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2):
  mu = 4e+10
  dinsm2Nsm = 1e-5
  alpha = 2/3
  length = 10 ** (0.440 * eq_mags - 1.289) # Riznichenko's formulas
  width = 10 ** (0.401 * eq_mags - 1.448)
  square = length * width * 1000 * 1000 # Focal area(m)

  eq_slip = (eq_moments * dinsm2Nsm) / (mu * square) # Seismic moment formula

  eq_first_al1 = length / 2
  eq_first_al2 = length - eq_first_al1
  eq_first_al1 = (-1) * eq_first_al1

  eq_first_aw1 = width / 2
  eq_first_aw2 = width - eq_first_aw1

  eq_second_al1 = length / 2
  eq_second_al2 = length - eq_second_al1
  eq_second_al1 = (-1) * eq_second_al1

  eq_second_aw1 = width / 2
  eq_second_aw2 = width - eq_second_aw1

  dip1_length = eq_depths - eq_first_aw2 * math.sin(math.radians(eq_dips1))
  dip2_length = eq_depths - eq_second_aw2 * math.sin(math.radians(eq_dips2))

  if dip1_length < 0:
    dip1_overlength = abs(dip1_length) / math.sin(math.radians(eq_dips1))
    eq_first_aw2 -= dip1_overlength
    eq_first_aw1 += dip1_overlength
  eq_first_aw1 = (-1) * eq_first_aw1

  if dip2_length < 0:
    dip2_overlength = abs(dip2_length) / math.sin(math.radians(eq_dips2))
    eq_second_aw2 -= dip2_overlength
    eq_second_aw1 += dip2_overlength
  eq_second_aw1 = (-1) * eq_second_aw1

  eq_first_u1 = eq_slip * math.cos(math.radians(eq_rakes1))
  eq_first_u2 = eq_slip * math.sin(math.radians(eq_rakes1))
  eq_first_u3 = 0  # Because we study earthquakes, not explosions (for earthquakes there is no vertical component of slip)

  eq_second_u1 = eq_slip * math.cos(math.radians(eq_rakes2))
  eq_second_u2 = eq_slip * math.sin(math.radians(eq_rakes2))
  eq_second_u3 = 0  # Because we study earthquakes, not explosions (for earthquakes there is no vertical component of slip)

  okada_flag = 1
  if okada_flag == 1:
    N_range = point_lat - eq_lats
    E_range = point_lon - eq_lons

    N_range = N_range * 111.13486
    E_range = E_range * math.cos(math.radians(eq_lats)) * 111.13486

    first_x = E_range * math.sin(math.radians(eq_strikes1)) + N_range * math.cos(math.radians(eq_strikes1))
    first_y = (-1) * E_range * math.cos(math.radians(eq_strikes1)) + N_range * math.sin(math.radians(eq_strikes1))
    first_z = 0

    second_x = E_range * math.sin(math.radians(eq_strikes2)) + N_range * math.cos(math.radians(eq_strikes2))
    second_y = (-1) * E_range * math.cos(math.radians(eq_strikes2)) + N_range * math.sin(math.radians(eq_strikes2))
    second_z = 0

    exist_eqpar_flag = 1
    if not open("eq_params", "w"):
      print("Can't open file with eq_parameters for first plane. Proceeding with the next offset...")
      exist_eqpar_flag = 0

    if exist_eqpar_flag == 1:
      with open("eq_params", "w") as eqpar:
        eqpar.write(str(first_x) + "\n")
        eqpar.write(str(first_y) + "\n")
        eqpar.write(str(first_z) + "\n")
        eqpar.write(str(eq_depths) + "\n")
        eqpar.write(str(eq_dips1) + "\n")
        eqpar.write(str(eq_first_al1) + "\n")
        eqpar.write(str(eq_first_al2) + "\n")
        eqpar.write(str(eq_first_aw1) + "\n")
        eqpar.write(str(eq_first_aw2) + "\n")
        eqpar.write(str(eq_first_u1) + "\n")
        eqpar.write(str(eq_first_u2) + "\n")
        eqpar.write(str(eq_first_u3) + "\n")

    exe_file_path = os.path.join(os.getcwd(), "okada.py")
    if os.path.exists(exe_file_path):
      print(f"Path to file: {exe_file_path}")
    else:
      print("File not found")
    subprocess.call(["python", exe_file_path])

    res = open("eq_stn_disp", "r")
    line = res.readline()
    line = line.split()
    ux_1= line[0]
    uy_1 = line[1]
    uz_1 = line[2]
    print(f"ux1 {ux_1}, uy1 {uy_1}, uz1 {uz_1}")

    exist_eqpar_flag = 1
    if not open("eq_params", "w"):
      print("Can't open file with eq_parameters for first plane. Proceeding with the next offset...")
      exist_eqpar_flag = 0

    if exist_eqpar_flag == 1:
      with open("eq_params", "w") as eqpar:
        eqpar.write(str(second_x) + "\n")
        eqpar.write(str(second_y) + "\n")
        eqpar.write(str(second_z) + "\n")
        eqpar.write(str(eq_depths) + "\n")
        eqpar.write(str(eq_dips2) + "\n")
        eqpar.write(str(eq_second_al1) + "\n")
        eqpar.write(str(eq_second_al2) + "\n")
        eqpar.write(str(eq_second_aw1) + "\n")
        eqpar.write(str(eq_second_aw2) + "\n")
        eqpar.write(str(eq_second_u1) + "\n")
        eqpar.write(str(eq_second_u2) + "\n")
        eqpar.write(str(eq_second_u3) + "\n")

    exe_file_path = os.path.join(os.getcwd(), "okada.py")
    if os.path.exists(exe_file_path):
      print(f"Path to file: {exe_file_path}")
    else:
      print("File not found")
    subprocess.call(["python", exe_file_path])

    res = open("eq_stn_disp", "r")
    line = res.readline()
    line = line.split()
    ux_2 = line[0]
    uy_2 = line[1]
    uz_2 = line[2]
    print(f"ux2 {ux_2}, uy2 {uy_2}, uz2 {uz_2}")

  return ux_1, uy_1, uz_1, ux_2, uy_2, uz_2


def get_data(point_lat_start, point_lat_end, point_lon_start, point_lon_end, h):
  lat_arr = np.arange(point_lat_start, point_lat_end + 0.01, h)
  lon_arr = np.arange(point_lon_start, point_lon_end + 0.01, h)

  file = open("results.txt", "w")
  eq_dates, eq_lats, eq_lons, eq_depths, eq_mags, eq_moments, eq_strikes1, eq_dips1, eq_rakes1, eq_strikes2, eq_dips2, eq_rakes2 = quakes()

  for i in range(len(eq_dates)):
    ux_1, uy_1, uz_1, ux_2, uy_2, uz_2 = [], [], [], [], [], []
    lat, lon = [], []
    for point_lat in lat_arr:
      for point_lon in lon_arr:
        lat.append(point_lat), lon.append(point_lon)
        ux1, uy1, uz1, ux2, uy2, uz2 = run_program(point_lat, point_lon, eq_dates[i], eq_lats[i], eq_lons[i], eq_depths[i], eq_mags[i], eq_moments[i], eq_strikes1[i], eq_dips1[i], eq_rakes1[i], eq_strikes2[i], eq_dips2[i], eq_rakes2[i])
        ux_1.append(ux1), uy_1.append(uy1), uz_1.append(uz1), ux_2.append(ux2), uy_2.append(uy2), uz_2.append(uz2)
    line1 = 'lat = {}\n'.format(lat)
    line2 = 'lon = {}\n'.format(lon)
    line3 = 'ux_1 = {}\n'.format(ux_1)
    line4 = 'uy_1 = {}\n'.format(uy_1)
    line5 = 'uz_1 = {}\n'.format(uz_1)
    line6 = 'ux_2 = {}\n'.format(ux_2)
    line7 = 'uy_2 = {}\n'.format(uy_2)
    line8 = 'uz_2 = {}\n'.format(uz_2)
    file.write(line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8)
  file.close()


def parse_file(file_name):
  num_lines = sum(1 for line in open(file_name))  # Counting the number of lines in a file
  date = np.empty(num_lines // 5, dtype='<U10')
  time = np.empty_like(date)
  lat = np.empty_like(date)
  lon = np.empty_like(date)
  depth = np.empty_like(date)
  scalar_moment = np.empty(num_lines // 5)
  sdr = np.empty(num_lines // 5, dtype='<U100')
  name_station = np.empty(num_lines // 5, dtype='<U100')
  num = np.empty(num_lines // 5, dtype='<U100')

  k = 0
  count = 0
  exponent = 0
  with open(file_name, 'r') as file:
    for i, line in enumerate(file):
      if k == 0:
        date[count] = line[5:15]
        time[count] = line[16:26]
        lat[count] = line[27:33]
        lon[count] = line[34:41]
        depth[count] = line[42:47]
        name_station[count] = line[56:-2]
      if k == 1:
        num[count] = line[0:8]
      if k == 3:
        exponent = float(line[0:2])
      if k == 4:
        scalar_moment[count] = float(line[49:56]) * 10**exponent
        sdr[count] = line[57:80]
        count += 1
      k += 1
      if k == 5:
        k = 0
  return date, time, lat, lon, depth, scalar_moment, sdr, name_station, num


if __name__ == "__main__":
  file_path = input("Enter the name of the earthquake catalog: ")

  Mw_s = float(input("Enter the lower limit of the magnitudes: "))
  Mw_e = float(input("Enter the upper limit of the magnitudes: "))
  lat_s = float(input("Enter the lower limit of the latitude: "))
  lat_e = float(input("Enter the upper limit of the latitude: "))
  lon_s = float(input("Enter the lower limit of the longitude: "))
  lon_e = float(input("Enter the upper limit of the longitude: "))
  h = float(input("Enter the step h with which you want to traverse the grid: "))  

  date, time, lat, lon, depth, scalar_moment, sdr, name_station, num = parse_file(file_path)

  res_file = open('DAILY_eqs.txt', 'w')
  res_file.write(f'###### {Mw_s}<=Mw<={Mw_e}, {lat_s}<=lat<={lat_e}, {lon_s}<=lon<={lon_e} ######\n')
  res_file.write(f'###### year month day time lat lon depth Mw scalar_moment strike1 dip1 rake1 strike2 dip2 rake2 ######\n')

  for i in range(len(date)):
    if Mw_s <= (2/3) * (np.log10(scalar_moment[i]) - 16.1) <= Mw_e and lat_s <= float(lat[i]) <= lat_e and lon_s <= float(lon[i]) <= lon_e:
      str_sdr = np.array(sdr[i].split())
      res_file.write(f'{date[i][0:4]} {date[i][5:7]} {date[i][8:10]} {time[i]} {lat[i]} {lon[i]} '
                     f'{depth[i]} {round((2 / 3) * (np.log10(scalar_moment[i]) - 16.1), 1)} '
                     f'{"{:.2e}".format(scalar_moment[i])} {str_sdr[0]} {str_sdr[1]} {str_sdr[2]} {str_sdr[3]} {str_sdr[4]} {str_sdr[5]} {num[i]} {name_station[i]}\n')
  res_file.close()

  get_data(lat_s, lat_e, lon_s, lon_e, h)

  file_path_GAO = os.path.join(os.getcwd(), "GraphicsAfterOkada.py")
  subprocess.call(["python", file_path_GAO, str(lat_s), str(lat_e), str(lon_s), str(lon_e), str(h)])

  subprocess.run(['rm', 'eq_params', 'eq_stn_disp'])
 
  file_path_DBM = os.path.join(os.getcwd(), "DrawBeachballMap.py")
  subprocess.call(["python", file_path_DBM, str(lat_s), str(lat_e), str(lon_s), str(lon_e), str(h)]) 
