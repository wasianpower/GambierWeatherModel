######################
## TEMPERATURE DATA ##
######################
#TMIN - Minimum temperature
#TMAX - Maximum temperature
#TOBS - Temperature at the time of observation

########################
## PRECIPITATION DATA ##
########################
#PRCP - Precipitation
#SNOW - Snowfall
#WESF - Water equivalent of snowfall
#SNWD - Snow depth
#WESD - Water equivalent of snow on the ground
#DASF - Number of days included in the multiday snow fall total (MDSF)
#MDSF - Multiday snowfall total
#DAPR - Number of days included in the multiday precipitation total (MDPR)
#MDPR - Multiday precipitation total (use with DAPR and DWPR, if available)

###################
## MISCELLANEOUS ##
###################
#WT01 - Fog, ice fog, or freezing fog (may include heavy fog)
#WT03 - Thunder
#WT04 - Ice pellets, sleet, snow pellets, or small hail
#WT05 - Hail (may include small hail)
#WT06 - Glaze or rime
#WT11 - High or damaging winds

#"STATION","NAME","DATE","DAPR","DASF","MDPR","MDSF","PRCP","SNOW","SNWD","TMAX","TMIN","TOBS","WESD","WESF","WT01","WT03","WT04","WT05","WT06","WT11"

import scipy.stats as st
import numpy

class date:
  def __init__(self,datestring : str):
    datetuple = [int(x) for x in datestring.replace("\"","").split("-")]
    self.month = datetuple[1]
    self.day = datetuple[2]

  def date_from_number(self,datenumber : int):
    month = 1
    while True:
      if month in [9,4,6,11]:
        if datenumber <= 30:
          break
        else:
          datenumber -= 30
      elif month == 2:
        if datenumber <= 28:
          break
        else:
          datenumber -= 28
      else:
        if datenumber <= 31:
          break
        else:
          datenumber -= 31
      month += 1
    self.date = datenumber
    self.month = month
  
  def is_between(self,day1,day2):
    #I'm a dumbass this could just convert day into total date and then go from there
    #day1 is start day, day2 is end day
    total = self.get_total_date()
    total1 = day1.get_total_date()
    total2 = day2.get_total_date()
    if total1 <= total2:
      if total1 <= total and total <= total2:
        return True
      else:
        return False
    else:
      if total1 < total:
        return True
      elif total < total2:
        return True
      else:
        return False

  def get_total_date(self):
    currmonth = 1
    total = 0
    while currmonth < self.month:
      if currmonth in [9,4,6,11]:
        total += 30
      elif currmonth == 2:
          total+=28
      else:
        total+=31
      currmonth += 1
    total+=self.day
    return total

def stdev(arr):
  return numpy.std(arr,ddof = 1)

def mean(arr):
  return numpy.mean(arr)

def pscore(avg,std,value):
  if std == 0:
    return 0
  z = (value - avg) / std
  p = st.norm.sf(z)
  return p


def rain(startday,endday,amount):
  with open("2716098.csv",'r') as f:
    data = [x.split(",") for x in f.readlines()]
  maxtemps = {}
  for row in data:
    #max temp index = 10, min temp index = 11
    #date index is 2
    thisdate = date(row[3])
    if thisdate.is_between(startday,endday):
      datenum = thisdate.get_total_date()
      if row[8] == "":
        point = 0
      else:
        point = float(row[8].replace("\"",""))
      if datenum in maxtemps:
        maxtemps[datenum].append(point)
      else:
        maxtemps[datenum] = [point]
  probarray = []
  snowdepth = amount
  totalmean = 0
  for day in maxtemps:
    todaydata = maxtemps[day]
    todaymean = mean(todaydata)
    totalmean += todaymean
    todaystd = stdev(todaydata)
    probarray.append(pscore(todaymean,todaystd,snowdepth))
  totalprob = 1
  for prob in probarray:
    totalprob *= (1 - prob)
  totalprob = 1 - totalprob
  totalmean = totalmean / len(probarray)
  adj = "low" if amount == .5 else "moderate" if amount==1 else "heavy"
  print("The odds of having at least one day in this range with at least " + str(amount) + " inches of rain ("+adj+" rainfall) is " + str("{:.2f}".format(totalprob * 100)) + "%")
  print("You can expect an average rainfall of " + str("{:.2f}".format(totalmean)) + " per day during this period.")

def lackofsnow(startday,endday,n):
  with open("2716098.csv",'r') as f:
    data = [x.split(",") for x in f.readlines()]
  maxtemps = {}
  for row in data:
    #max temp index = 10, min temp index = 11
    #date index is 2
    thisdate = date(row[3])
    if thisdate.is_between(startday,endday):
      datenum = thisdate.get_total_date()
      if row[10] == "":
        point = 0
      else:
        point = float(row[10].replace("\"",""))
      if datenum in maxtemps:
        maxtemps[datenum].append(point)
      else:
        maxtemps[datenum] = [point]
  probarray = []
  snowdepth = 0
  totalmean = 0
  for day in maxtemps:
    todaydata = maxtemps[day]
    todaymean = mean(todaydata)
    totalmean += todaymean
    todaystd = stdev(todaydata)
    probarray.append(pscore(todaymean,todaystd,snowdepth))
  totalprob = 1
  for prob in probarray:
    totalprob *= prob
  totalprob = 1 - totalprob
  totalmean = totalmean / len(probarray)
  print("The odds of having no snow on the ground for at least one day in this range is " + str("{:.2f}".format(totalprob * 100)) + "%")
  print("You can expect an average snow depth of " + str("{:.2f}".format(totalmean)) + " inches during this period.")

def highwarmness(startday,endday,n):
  with open("2716098.csv",'r') as f:
    data = [x.split(",") for x in f.readlines()]
  maxtemps = {}
  for row in data:
    #max temp index = 10, min temp index = 11
    if row[11] == "": continue
    #date index is 2
    thisdate = date(row[3])
    if thisdate.is_between(startday,endday):
      datenum = thisdate.get_total_date()
      if datenum in maxtemps:
        maxtemps[datenum].append(int(row[11].replace("\"","")))
      else:
        maxtemps[datenum] = [int(row[11].replace("\"",""))]
  print("The odds of getting at least one day in the given day range with a high temperature of at least")
  hugemean = 0
  for temp in range(0,100):
    totalmean = 0
    probarray = []
    for day in maxtemps:
      todaydata = maxtemps[day]
      todaymean = mean(todaydata)
      totalmean += todaymean
      todaystd = stdev(todaydata)
      probarray.append(pscore(todaymean,todaystd,temp))
    totalprob = 1
    totalmean = totalmean / len(probarray)
    hugemean += totalmean
    for prob in probarray:
      totalprob *= (1 - prob)
    totalprob = 1 - totalprob
    print(str(temp) + " degrees: " + str("{:.2f}".format(totalprob * 100)) + "%")
  hugemean = hugemean / 100
  print("The average high temperature during this period is " + str("{:.2f}".format(hugemean)) + " degrees.")
  print("All temperatures in Farenheit.")



def lowwarmness(startday,endday,n):
  with open("2716098.csv",'r') as f:
    data = [x.split(",") for x in f.readlines()]
  maxtemps = {}
  for row in data:
    #max temp index = 10, min temp index = 11
    if row[12] == "": continue
    #date index is 2
    thisdate = date(row[3])
    if thisdate.is_between(startday,endday):
      datenum = thisdate.get_total_date()
      if datenum in maxtemps:
        maxtemps[datenum].append(int(row[12].replace("\"","")))
      else:
        maxtemps[datenum] = [int(row[12].replace("\"",""))]
  print("The odds of getting at least one day in the given day range with a low temperature of at least")
  hugemean = 0
  for temp in range(0,100):
    totalmean = 0
    probarray = []
    for day in maxtemps:
      todaydata = maxtemps[day]
      todaymean = mean(todaydata)
      totalmean += todaymean
      todaystd = stdev(todaydata)
      probarray.append(pscore(todaymean,todaystd,temp))
    totalprob = 1
    totalmean = totalmean / len(probarray)
    hugemean += totalmean
    for prob in probarray:
      totalprob *= (1 - prob)
    totalprob = 1 - totalprob
    print(str(temp) + " degrees: " + str("{:.2f}".format(totalprob * 100)) + "%")
  hugemean = hugemean / 100
  print("The average low temperature during this period is " + str("{:.2f}".format(hugemean)) + " degrees.")
  print("All temperatures in Farenheit.")
  



def get_range():
  startday = date(input("Enter start date in the form year-month-day, for example, for September 10th, 2021, you would enter 2021-09-10: \n"))
  endday = date(input("Enter end date in the same format (note: total time between start and end date can not be more than 365 days): \n"))
  return startday,endday


def main():
  try:
    startday,endday=get_range()
    mode = int(input("Enter the mode you are looking for:\n1: Warm Days\n2: Days with no snow on ground\n3: Days with rain\n"))
  except:
    print("invalid input.")
    exit()
  #howmany = int(input("Enter how many days you need with that quality: "))
  if mode == 1:
    submode = 0
    while not submode in ("1","2","3"):
      submode = input("Enter the mode you would like the model to use:\n1: High Temperature (recommended)\n2: Low Temperature\n")
    submode = int(submode)
    if submode == 1:
      highwarmness(startday,endday,1)
    elif submode == 2:
      lowwarmness(startday,endday,1)
  elif mode == 2:
    lackofsnow(startday,endday,1)
  elif mode == 3:
    submode = 0
    while not submode in ("1","2","3"):
      submode = input("Are you looking for a day with rain that is \n1: Light\n2: Medium\n3: Heavy\n")
    rain(startday,endday,int(submode)/2)


main()