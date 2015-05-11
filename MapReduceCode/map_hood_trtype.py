#!/usr/bin/env python
###############################################################################

##
###############################################################################


import csv,sys,os
os.environ['MPLCONFIGDIR'] = '/tmp'
import numpy
from matplotlib.path import Path
from rtree import index as rtree
import shapefile  
from pyproj import Proj, transform
import math
from datetime import datetime
import numpy, shapefile, time

def findNeighborhood(location, index, neighborhoods):
    match = index.intersection((location[0], location[1], location[0], location[1]))
    for a in match:
        if any(map(lambda x: x.contains_point(location), neighborhoods[a][1])):
            return a
    return -1

def readNeighborhood(shapeFilename, index, neighborhoods):
    sf = shapefile.Reader(shapeFilename)
    for sr in sf.shapeRecords():
        if sr.record[1] not in ['New York', 'Kings', 'Queens', 'Bronx']: continue
        paths = map(Path, numpy.split(sr.shape.points, sr.shape.parts[1:]))
        bbox = paths[0].get_extents()
        map(bbox.update_from_path, paths[1:])
        index.insert(len(neighborhoods), list(bbox.get_points()[0])+list(bbox.get_points()[1]))
        neighborhoods.append((sr.record[3], paths))
    neighborhoods.append(('UNKNOWN', None))

def parseInput():
    for line in sys.stdin:
        line = line.strip('\n')
        values = line.split(',')
        if len(values)>1 and values[0]!='medallion': 
            yield values

def geocode(longitude,latitude,index_rtree,neighborhoods):
    if not latitude or not longitude:
        #print("Error reading longitude/latitude")
        return -1

    #convert to projected
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:26918')
    outx,outy = transform(inProj,outProj,longitude,latitude)
    pickup_location = (outx,outy)

    resultMap = findNeighborhood(pickup_location, index_rtree, neighborhoods)
    if resultMap!=-1:
        zipcode_result = neighborhoods[resultMap][0]
        return zipcode_result
    else:
        #print("Unable to convert lat-lon: %f %f"%(float(latitude),float(longitude)))
        return -1


def main():
    index_rtree = rtree.Index()
    neighborhoods = []
    agg = {}
    readNeighborhood('ZillowNeighborhoods-NY.shp', index_rtree, neighborhoods)

    for values in parseInput():
    
        try:
            #general trips attributes
            pickup_datetime = values[0]
            dropoff_datetime = values[1]
            # print(type(pickup_datetime))
	    pickup_date = datetime.strptime(values[0], '%Y-%m-%d %H:%M:%S')
	    #print(pickup_date)
	    #dropoff_date = datetime.strptime(dropoff_datetime, '%Y-%m-%d %H:%M:%S')
	    #year = datetime.strftime(date, '%Y')
            month = datetime.strftime(pickup_date, '%m')
            day = datetime.strftime(pickup_date, '%d')
            hour = datetime.strftime(pickup_date, '%H')
	    #print(month,day,hour)
	    passenger_count = values[2]
            trip_time_in_secs = values[3]
            trip_distance = values[4]
            pickup_longitude = values[5]
            pickup_latitude = values[6]
            dropoff_longitude = values[7]
            dropoff_latitude = values[8]
	    payment_type=values[9]
            fare_amount = values[10]
            tip_amount = values[11]
            total_amount = values[12]
            tip_percentage = ((float(tip_amount)/float(fare_amount))*100)
        
            #attributes for geocoding       
            pickup_location = (float(pickup_longitude), float(pickup_latitude))
            dropoff_location = (float(dropoff_longitude), float(dropoff_latitude))
            pickup_location = (float(values[5]), float(values[6]))
            pickup_neighborhood = findNeighborhood(pickup_location, index_rtree, neighborhoods)
            dropoff_location = (float(values[7]), float(values[8]))
            dropoff_neighborhood = findNeighborhood(dropoff_location, index_rtree, neighborhoods)
            if pickup_neighborhood!=-1:
                pickup_hood = neighborhoods[pickup_neighborhood][0]
            else:
                pickup_hood = ''
            if dropoff_neighborhood!=-1:
                dropoff_hood = neighborhoods[dropoff_neighborhood][0]
            else:
                dropoff_hood = ''
            if (pickup_neighborhood!=-1) and (dropoff_neighborhood!=-1):
               print '%s\t%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (pickup_hood+'^'+dropoff_hood,pickup_datetime,month,day,hour,dropoff_datetime,passenger_count,trip_time_in_secs,trip_distance,\
                                                                fare_amount, tip_amount, total_amount, tip_percentage,pickup_hood,dropoff_hood,payment_type)
        except:
            pass



if __name__ == '__main__':
    main()
