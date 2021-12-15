from types import LambdaType
import pandas
import pyproj

class DistSet():
    def __init__(self, refpts, assesspts):
        self.refpts = pandas.DataFrame(refpts)
        self.assesspts = pandas.DataFrame(assesspts)
        self.geodist = self.geoDist()
        self.mapdist = self.mapDist()

    def geoDist(self):
        geod = pyproj.Geod(ellps="WGS84")
        data = []
        for i,row1 in self.refpts.iterrows():
            lon1 = row1['lon_dec']
            lat1 = row1['lat_dec']
            for i,row2 in self.assesspts.iterrows():
                lon2 = row2['lon_dec']
                lat2 = row2['lat_dec']
                result = geod.inv(lon1,lat1,lon2,lat2)
                corr_fwd = 0
                if result[0] < 0:
                    corr_fwd = 360
                corr_bck = 0
                if result[1] < 0:
                    corr_bck = 360
                data.append((result[0]+corr_fwd,result[1]+corr_bck,result[2]))
        return data
    
    def mapDist(self):
        pass