from types import LambdaType
import pandas
import pyproj
import math


class DistSet():
    def __init__(self, refpts, assesspts):
        self.refpts = pandas.DataFrame(refpts)
        self.assesspts = pandas.DataFrame(assesspts)
        self.dataframe = self.assesspts
        self.geod = pyproj.Geod(ellps="WGS84")
        for i, row in self.refpts.iterrows():
            self.dataframe[f"{row['id']} relation"] = self.posRelation(row)
            geodata = self.geoDist(row)
            self.dataframe[f"{row['id']} geo fwd"] = geodata[0]
            self.dataframe[f"{row['id']} geo bck"] = geodata[1]
            self.dataframe[f"{row['id']} geo dist"] = geodata[2]
            mapdata = self.mapDist(row)
            self.dataframe[f"{row['id']} map fwd"] = mapdata[0]
            self.dataframe[f"{row['id']} map bck"] = mapdata[1]
            self.dataframe[f"{row['id']} map dist"] = mapdata[2]

    def posRelation(self, refptrow):
        data = []
        for i, row in self.dataframe.iterrows():
            relation = ""
            if row['lat_dec'] > refptrow['lat_dec']:
                relation += "N"
            elif row['lat_dec'] < refptrow['lat_dec']:
                relation += "S"
            else:
                relation += "-"
            if row['lon_dec'] > refptrow['lon_dec']:
                relation += "E"
            elif row['lon_dec'] < refptrow['lon_dec']:
                relation += "W"
            else:
                relation += "-"
            data.append(relation)
        return data

    def geoDist(self, refptrow):
        data_fwd = []
        data_bck = []
        data_dist = []
        lon1 = refptrow['lon_dec']
        lat1 = refptrow['lat_dec']
        for i, row in self.dataframe.iterrows():
            lon2 = row['lon_dec']
            lat2 = row['lat_dec']
            result = self.geod.inv(lon1, lat1, lon2, lat2)
            corr_fwd = 0
            if result[0] < 0:
                corr_fwd = 360
            corr_bck = 0
            if result[1] < 0:
                corr_bck = 360
            data_fwd.append(result[0] + corr_fwd)
            data_bck.append(result[1] + corr_bck)
            data_dist.append(result[2])
        return (data_fwd, data_bck, data_dist)

    def mapDist(self, refptrow):
        data_fwd = []
        data_bck = []
        data_dist = []
        x1 = refptrow['UTM_east']
        y1 = refptrow['UTM_north']
        # # correct for grid convergence on ref pt
        # utm_zone_nr_ref = int(refptrow['UTM_zone'][:-1])
        # utm_meridian_ref = (utm_zone_nr_ref - 1) * 6 - 177
        # grid_convergence_ref = \
        #     math.degrees(math.atan(math.tan(refptrow['lon_dec'] - utm_meridian_ref)
        #                            * math.sin(refptrow['lat_dec'])))
        for i, row in self.dataframe.iterrows():
            x2 = row['UTM_east']
            y2 = row['UTM_north']
            if x1 == x2:
                same_x = True
            else:
                same_x = False
            # # correct for grid convergence on assess pt
            # utm_zone_nr_ass = int(row['UTM_zone'][:-1])
            # utm_meridian_ass = (utm_zone_nr_ass - 1) * 6 - 177
            # grid_convergence_ass = \
            #     math.degrees(math.atan(math.tan(row['lon_dec'] - utm_meridian_ass)
            #                            * math.sin(row['lat_dec'])))
            if same_x:
                fwd = 0
            else:
                fwd_radians = math.atan((y2 - y1) / (x2 - x1))
                fwd = 90 - math.degrees(fwd_radians)
            bck = fwd + 180
            # switch bearings around if refpt is east of assesspt
            if refptrow['UTM_east'] > row['UTM_east']:
                data_fwd.append(bck)
                data_bck.append(fwd)
            else:
                data_fwd.append(fwd)
                data_bck.append(bck)
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            data_dist.append(dist)
        return (data_fwd, data_bck, data_dist)
