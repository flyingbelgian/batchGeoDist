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
        # for i, row in self.refpts.iterrows():
        #     self.dataframe[f"{row['id']} relation"] = self.posRelation(row)
        #     geodata = self.geoDist(row)
        #     self.dataframe[f"{row['id']} geo fwd"] = geodata[0]
        #     self.dataframe[f"{row['id']} geo bck"] = geodata[1]
        #     self.dataframe[f"{row['id']} geo dist"] = geodata[2]
        #     mapdata = self.mapDist(row)
        #     self.dataframe[f"{row['id']} map fwd"] = mapdata[0]
        #     self.dataframe[f"{row['id']} map bck"] = mapdata[1]
        #     self.dataframe[f"{row['id']} map dist"] = mapdata[2]

    def posRelation(coord_DD_1: tuple, coord_DD_2: tuple):
        '''Takes 2 coordinate tuples (lat, lon), returns a string expressing relative location'''
        relation = ""
        if coord_DD_2[0] > coord_DD_1[0]:
            relation += "N"
        elif coord_DD_2[0] < coord_DD_1[0]:
            relation += "S"
        if coord_DD_1[1] > coord_DD_2[1]:
            relation += "W"
        elif coord_DD_1[1] < coord_DD_2[1]:
            relation += "E"
        return relation

    def geoDist(coord_DD_1: tuple, coord_DD_2: tuple, geod: pyproj.Geod):
        '''Takes 2 coordinate tuples (lat,lon) and geod definition, \
           returns tuple with relational info, avoiding negative bearings'''
        result = geod.inv(coord_DD_1[1], coord_DD_1[0], coord_DD_2[1], coord_DD_2[0])
        if result[0] < 0:
            result[0] += 360
        if result[1] < 0:
            result[1] += 360
        return result

    def mapDist(coord_UTM_1: tuple, coord_UTM_2: tuple, UTM_zone: string):
        '''Takes 2 coordinate tuples (northing,easting) and UTM zone (string), \
           returns tuple with relational info, corrected for projection errors in bearing and distance. \
           Distance correction uses Sympson method'''
        x1 = coord_UTM_1[1]
        y1 = coord_UTM_1[0]
        x2 = coord_UTM_2[1]
        y2 = coord_UTM_2[0]
        utm_zone_nr = int(UTM_zone[:-1])
        utm_meridian = utm_zone_nr * 6 - 183
        # gridconvergenceref = math.degrees(math.atan(math.tan(refptrow['lon_dec']-utmmeridianref) * math.sin(refptrow['lat_dec'])))
        # #correct for grid convergence on assess pt
        # utmzoneassess = int(row['UTM_zone'][:-1])
        # utmmeridianassess = (utmzoneassess-1) * 6 - 177
        # gridconvergenceassess = math.degrees(math.atan(math.tan(row['lon_dec']-utmmeridianassess) * math.sin(row['lat_dec'])))
        fwd_radians = math.atan((y2 - y1) / (x2 - x1))
        fwd_raw = 90 - math.degrees(fwd_radians)
        bck_raw = fwd_raw + 180
        if x1 < x2:  # use raw values if point 1 ir west of point 2
            fwd = fwd_raw
            bck = bck_raw
        else:  # switch bearings if point 1 is east of point 2
            fwd = bck_raw
            bck = fwd_raw
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return (fwd, bck, dist)
