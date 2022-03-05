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
        '''Takes row of data and returns string with relative compass direction \
        from assess point to reference point.'''
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
        '''Takes row of data and returns tuple with fwd and bck bearings and distance'''
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
        '''Takes row of data and returns tuple with fwd and bck bearings and distance \
        measured from UTM coordinates and corrected for grid convergence'''
        data_fwd = []
        data_bck = []
        data_dist = []
        x1 = refptrow['UTM_east']
        y1 = refptrow['UTM_north']
        # correct for grid convergence on ref pt
        utm_zone_nr_ref = int(refptrow['UTM_zone'][:-1])
        utm_meridian_ref = utm_zone_nr_ref * 6 - 183
        lon_ref_rad = math.radians(refptrow['lon_dec'] - utm_meridian_ref)
        lon_ref_tan = math.tan(lon_ref_rad)
        lat_ref_rad = math.radians(refptrow['lat_dec'])
        lat_ref_sin = math.sin(lat_ref_rad)
        grid_convergence_ref = math.degrees(math.atan(lon_ref_tan * lat_ref_sin))
        for i, row in self.dataframe.iterrows():
            x2 = row['UTM_east']
            y2 = row['UTM_north']
            if x1 == x2:
                same_x = True
            else:
                same_x = False
            # correct for grid convergence on assess pt
            utm_zone_nr_ass = int(row['UTM_zone'][:-1])
            utm_meridian_ass = utm_zone_nr_ass * 6 - 183
            lon_ass_rad = math.radians(row['lon_dec'] - utm_meridian_ass)
            lon_ass_tan = math.tan(lon_ass_rad)
            lat_ass_rad = math.radians(row['lat_dec'])
            lat_ass_sin = math.sin(lat_ass_rad)
            grid_convergence_ass = math.degrees(math.atan(lon_ass_tan * lat_ass_sin))
            if same_x:
                fwd_slope = 0
            else:
                fwd_radians = math.atan((y2 - y1) / (x2 - x1))
                fwd_slope = 90 - math.degrees(fwd_radians)
            bck_slope = fwd_slope + 180
            # switch bearings around if refpt is east of assesspt
            if refptrow['UTM_east'] > row['UTM_east']:
                fwd_bearing = bck_slope
                bck_bearing = fwd_slope
            else:
                fwd_bearing = fwd_slope
                bck_bearing = bck_slope
            fwd_bearing_corrected = fwd_bearing + grid_convergence_ref
            bck_bearing_corrected = bck_bearing + grid_convergence_ass
            data_fwd.append(fwd_bearing_corrected)
            data_bck.append(bck_bearing_corrected)
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            data_dist.append(dist)
        return (data_fwd, data_bck, data_dist)
