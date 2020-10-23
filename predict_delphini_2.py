import math
import time
import datetime
import ephem
import matplotlib
import matplotlib.pyplot as plt
import os
import numpy as np
import urllib2
import numpy
import urllib
import os
from PIL import Image
from dateutil import tz
import sys

if len(sys.argv) > 1:
        try:
		date = datetime.datetime.utcfromtimestamp(int(sys.argv[1]))
		#print date
        except:
		date = datetime.datetime.strptime(str(sys.argv[1]).replace("T", " "), '%Y-%m-%d %H:%M:%S')
else:	
	date = datetime.datetime.strptime(str(datetime.datetime.utcnow()).split(".")[0], '%Y-%m-%d %H:%M:%S')	

# METHOD 2: Auto-detect zones:
from_zone = tz.tzutc()
to_zone = tz.tzlocal()
u = 3.986004418**14
er=6371.

#Location of Ground station
lat_obs = "56.1718" #latitude of the observatory
lon_obs = "10.19" #longitude of the observatory with base "west"
elev_obs = 50 #elevation of the observatory

degrees_per_radian = 180.0 / math.pi
home = ephem.Observer()
home.lon = lon_obs   # +E
home.lat = lat_obs      # +N
home.elevation = elev_obs # meters

# Get the latest TLE of Delphini-1 (CATNR=44030)
delphini_tle_norad_url = "https://celestrak.com/satcat/tle.php?CATNR=44030"
resp = urllib2.urlopen(delphini_tle_norad_url)
page = resp.read()
name,tle1,tle2,bla = page.split("\r\n")

# Plotting things to make live update to graph
fig = plt.figure(figsize=(15.0, 10.0),facecolor='k', edgecolor='k')
plt.subplots_adjust(left=0.05, bottom=0.05, right=0.99, top=0.95, wspace=0.0, hspace=0.0)
ax = fig.add_subplot(111)
plt.style.use('dark_background')



# GET NORAD TLE for Delphini-1
resp = urllib2.urlopen(delphini_tle_norad_url)
page = resp.read()
name,tle1,tle2,bla = page.split("\r\n")
delphini = ephem.readtle('Delphini', tle1, tle2)

os.popen("xplanet -projection rectangular -date %s -config mfa_config.txt -latitude 0.0 -longitude 0.0 -geometry 1600x1000 -output /home/mads-guest/Skrivebord/delphini_predict.jpg -num_times 1" % (str(date).replace("-", "").replace(" ", ".").replace(":","")))
new_im = Image.open("/home/mads-guest/Skrivebord/delphini_predict.jpg")

# Create passed and future trajectories
passed_lat = []
passed_lon = []
future_lat = []
future_lon = []

pass_lat = []
pass_lon = []

dt_passed = range(0,30*60,10) # 30 minutes
dt_future = range(0,30*60,10) # 30 minutes
for seconds in dt_passed:
	home.date = date-datetime.timedelta(seconds=(dt_passed[-1]-seconds))
	delphini.compute(home)	

	if str(delphini.sublat)[0] == "-": sign_lat = -1 
	else: sign_lat = 1
	if str(delphini.sublong)[0] == "-": sign_long = -1 
	else: sign_long = 1	
	passed_lat.append(sign_lat * (abs(float(str(delphini.sublat).split(":")[0])) + float(str(delphini.sublat).split(":")[1])/60.+float(str(delphini.sublat).split(":")[2])/3600.) + 90.)
	passed_lon.append((sign_long * (abs(float(str(delphini.sublong).split(":")[0])) + float(str(delphini.sublong).split(":")[1])/60.+float(str(delphini.sublong).split(":")[2])/3600.))+180.)

for seconds in dt_future:
	home.date = date+datetime.timedelta(seconds=seconds)
	delphini.compute(home)	

	if str(delphini.sublat)[0] == "-": sign_lat = -1 
	else: sign_lat = 1
	if str(delphini.sublong)[0] == "-": sign_long = -1 
	else: sign_long = 1	
	future_lat.append(sign_lat * (abs(float(str(delphini.sublat).split(":")[0])) + float(str(delphini.sublat).split(":")[1])/60.+float(str(delphini.sublat).split(":")[2])/3600.) + 90.)
	future_lon.append((sign_long * (abs(float(str(delphini.sublong).split(":")[0])) + float(str(delphini.sublong).split(":")[1])/60.+float(str(delphini.sublong).split(":")[2])/3600.))+180.)

	if (delphini.alt) > 0.:
		pass_lat.append(sign_lat * (abs(float(str(delphini.sublat).split(":")[0])) + float(str(delphini.sublat).split(":")[1])/60.+float(str(delphini.sublat).split(":")[2])/3600.) + 90.)
		pass_lon.append((sign_long * (abs(float(str(delphini.sublong).split(":")[0])) + float(str(delphini.sublong).split(":")[1])/60.+float(str(delphini.sublong).split(":")[2])/3600.))+180.)


# Calculate current position of Delphini-1 and values seen from the ground station 
home.date = date	
delphini.compute(home)
#datetime.datetime.strptime(str(delphini.set_time), '%Y/%m/%d %H:%M:%S')

if str(delphini.sublat)[0] == "-": sign_lat = -1 
else: sign_lat = 1
if str(delphini.sublong)[0] == "-": sign_long = -1 
else: sign_long = 1

del_lat = sign_lat * (abs(float(str(delphini.sublat).split(":")[0])) + float(str(delphini.sublat).split(":")[1])/60.+float(str(delphini.sublat).split(":")[2])/3600.)
del_lon = sign_long * (abs(float(str(delphini.sublong).split(":")[0])) + float(str(delphini.sublong).split(":")[1])/60.+float(str(delphini.sublong).split(":")[2])/3600.)


utc_time = datetime.datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')
utc_time = utc_time.replace(tzinfo=from_zone)
local_time = str(utc_time.astimezone(to_zone)).split("+")[0]

#print (date  - datetime.datetime(1970, 1, 1)).total_seconds()
if (datetime.datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S') - datetime.datetime.utcnow()).total_seconds() > 0:
	unix_time = time.time() + (datetime.datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')-datetime.datetime.utcnow()).total_seconds()
else:
	unix_time = time.time() - (datetime.datetime.utcnow()-datetime.datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')).total_seconds()


print utc_time
print int(unix_time)

# Plot the shit...
ax.imshow(new_im, extent=[0, 360, 0, 180])
ax.plot(passed_lon, passed_lat,"w.", markersize=1)
ax.plot(future_lon, future_lat,"w.", markersize=1)

if len(pass_lat) > 0:
	ax.plot(pass_lon, pass_lat,".", color="lime", markersize=2)

ax.scatter(del_lon+180.,del_lat+90., s=100, c="lime", edgecolors="black", linewidth=2)
plt.text(del_lon+180.+1,del_lat+90.+1, "Delphini-1", color="white")
#plt.text(del_lon+180.+1,del_lat+90.+1, "Image number 1925", color="white")
print("Longitude: %s" % (str(del_lon)))
print("Latitude: %s" % (str(del_lat)))

ax.scatter(22.+180.,45.5+90.+1, s=1500, c="pink", edgecolors="red", linewidth=1, alpha=0.6)

plt.xticks([0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360], ("-180", "-160", "-140", "-120", "100", "-80", "-60", "-40", "-20", "0" , "20", "40", "60", "80", "100", "120", "140", "160", "180"))
plt.yticks([0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180], ("-90", "-75", "-60", "-45" , "-30", "-15", "0", "15", "30", "45", "60", "75", "90"))

plt.title("Delphini-1 info at\n%s UTC\n%s CET\nUnix time: %i" % (str(date).split(".")[0], local_time, int(unix_time)) , color="white", size=20)
fig.patch.set_facecolor('black')
ax.tick_params(axis='both', colors='white')
plt.xlabel("Longitude", color="white")
plt.ylabel("Latitude", color="white")
plt.xlim([0.0,360.])
plt.ylim([0.0,180.])
plt.rcParams['figure.facecolor'] = 'black'

ax.tick_params(axis=u'both', which=u'both',length=0)
#fig.canvas.draw()
#plt.savefig("/tmp/delphini_plot.jpg", facecolor="black")
plt.show()
plt.cla()



