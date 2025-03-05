from datetime import datetime
import numpy as np


def convert_date_to_decimal(year, month, day, hour, minute): # Converting a date to decimal form
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

  return int(date.year), int(date.month), int(date.day), int(hour), int(minute)


def len_vector(x, y):
  return np.sqrt(x**2 + y**2)


def optimal_width(area, Mw):
  # widths = {
  #   12: 1e4,
  #   44: 3e4
  # }

  # width_ranges = {
  #   (0, 2): 0.5e3,
  #   (2, 4): 1e4,
  #   (4, 6): 1.5e4,
  #   (6, 8): 2e4,
  #   (8, 10): 2.5e4
  # }
  width_ranges = {
    (0, 2): 1e3,
    (2, 4): 2e4,
    (4, 6): 3e4,
    (6, 8): 4e4,
    (8, 10): 5e4
  }

  # for key in sorted(widths):
  #   if key >= area:
  #     return widths[key]
  for magnitude_range, width in width_ranges.items():
    if magnitude_range[0] <= Mw < magnitude_range[1]:
      return width

  # return 5e4  # Return default value for large areas
