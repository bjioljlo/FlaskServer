import pandas as pd

#Donchian Channel function
def DONCH(high, low ,  n = 20):
  array_high = high
  array_low = low
  # Function to caculate the high band
  def DchannelUpper(i):
      x = float(0.0)
      if(i < n):
          for j in range(i, -1, -1):
              x = max(array_high[j], x)
      else:
          for j in range(i, i-n, -1):
              x = max(array_high[j], x)
      return x

  # Function to caculate the low band


  def DchannelLower(i):
      x = float("inf")
      if(i < n):
          for j in range(i, -1, -1):
              x = min(array_low[j], x)
      else:
          for j in range(i, i-n, -1):
              x = min(array_low[j], x)
      return x


  # calculating the high band, n = 20

  array_upper = []
  for i in range(0, array_high.size):
      array_upper.append(DchannelUpper(i))

  #print("The high band is:")
  #print(array_upper)


  # calculating the low band, n = 20

  array_lower = []
  for i in range(0, array_low.size):
      array_lower.append(DchannelLower(i))

  #print("The low band is:")
  #print(array_lower)


  # calculating the mid band, n = 20

  array_middle = []
  for i in range(0, len(array_lower)):
      array_middle.append((array_upper[i]+array_lower[i])/2)

  #print("The mid band is:")
  #print(array_middle)

  df = pd.DataFrame(index=high.index)
  df['Highest_high'] = array_upper
  df['Lowest_low'] = array_lower
  df['Middle_band'] = array_middle
  return df['Highest_high'],df['Middle_band'],df['Lowest_low']

