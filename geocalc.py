from types import LambdaType
import pandas
import pyproj

class DistSet():
    def __init__(self, set1, set2):
        self.set1 = pandas.DataFrame(set1)
        self.set2 = pandas.DataFrame(set2)
        # print(set1)
        # print(set2)
    
    def greatCircle(self):
        geod = pyproj.Geod(ellps="WGS84")
        # result = geod.inv(151,34,151,33)
        # print(result)
        dist_data = []
        for i,row1 in self.set1.iterrows():
            lon1 = row1['lon_dec']
            lat1 = row1['lat_dec']
            for i,row2 in self.set2.iterrows():
                lon2 = row2['lon_dec']
                lat2 = row2['lat_dec']
                dist_data.append(geod.inv(lon1,lat1,lon2,lat2))
        print(dist_data)
