import ephem
import urllib.request
import numpy as np
from shapely.geometry import Polygon, Point
from datetime import datetime
#STUP{{{
# Get the latest tle, and create at sattelite object
def get_tle():
    delphini_tle_norad_url = "https://celestrak.com/satcat/tle.php?CATNR=44030"
    html=urllib.request.urlopen(delphini_tle_norad_url)
    string=str(html.read())
    return(tuple(string.split("\\r\\n")))

name,tle1,tle2,_=get_tle()
delphini = ephem.readtle('Delphini', tle1, tle2)

#}}}

# FUNCTIONS{{{

# Calculate the distance to the boundry of the shape object given
def dead_dist(t,shape):
    delphini.compute(t)
    #Convert the hours:min:seconds to useful units
    #Create a shaply shape-object and return the distance
    point=Point(float(repr(delphini.sublat))*(180/np.pi),float(repr(delphini.sublong))*(180/np.pi))
    x= shape.boundary.distance(point) if shape.boundary.distance(point)>0.05 else 0
    return(shape.boundary.distance(point))


# Distance to the shape, give 0 when delphini is in shape
def area_dist(t,shape):
    delphini.compute(t)
    #Convert the hours:min:seconds to useful units
    #Create a shaply shape-object and return the distance
    point=Point(float(repr(delphini.sublat))*(180/np.pi),float(repr(delphini.sublong))*(180/np.pi))
    return(shape.distance(point))

# Convert a ephem date to a epoch sends timestamp
def get_epoch(t):
    return(int((t-ephem.date('1970'))/ephem.second))
#}}}

# This section is to create the shape object{{{
lats=[]
lons=[]
with open('shape','r') as shape_file:
    for line in shape_file:
        if len(line.split())==2:
            data=line.strip().split()
            lats.append(float(data[0]))
            lons.append(float(data[1]))
path=list(zip(lats,lons))
# Create a shaply polygon from our points
ply=Polygon(path)

#}}}

print("This script will create a flightplan for tx inhibit above russia\nIt requeres 2 inputs:\n1. Filename - The filename for the created flighplan, deafauld is 'YYYmmdd'\n2. Days - nr. of days the created flighplan will last, deafault is 10")

# Get user input
file_name=str(input("Filename for created flightplan: ") or datetime.now().strftime("%Y%m%d"))
nr_days=int(input("Days: ") or 10)

# Lambda functions for calculatinf distances

#Dsitance to border
dst=lambda t: dead_dist(t,ply)

#Dsitance to shape, 0 when delphini is in shape
adst=lambda t: area_dist(t,ply)


# Predictions section
#Set start date to now
start_date=ephem.now()

#Keep track of fp command nr
N=0
#List of commands
out=[]
while start_date<ephem.now()+nr_days*24*ephem.hour:

# Find a time where delphini enters the area
    while adst(start_date)>0:
        start_date+=10*ephem.second
#FIND ENTRANCE
    d1=ephem.newton(dst,start_date-ephem.minute,start_date)
    delphini.compute(d1)
    y1,x1=(float(repr(delphini.sublat))*(180/np.pi),float(repr(delphini.sublong))*(180/np.pi))
    

#Find EXIT
    start_date+=240*ephem.second
    d2=ephem.newton(dst,start_date+ephem.minute,start_date)
    delphini.compute(d2)
    y2,x2=(float(repr(delphini.sublat))*(180/np.pi),float(repr(delphini.sublong))*(180/np.pi))
    start_date=d2+30*ephem.minute
    d1=get_epoch(d1)
    d2=get_epoch(d2)
    duration=d2-d1
    out.append("tx_inhibit{:d},rparam download 5 0,0,0,0,0,{:d},0,0".format(N,d1-4))
    out.append("tx_inhibit{:d},rparam set tx_inhibit {:d},0,0,0,0,{:d},0,0".format(N+1,duration,d1))
    N+=2

with open(file_name,'w') as out_file:
    out_file.writelines("%s\n" % item for item in out)
