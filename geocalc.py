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

        def gridConvergence(UTM_zone, lat_dec, lon_dec):
            utm_zone_nr = int(UTM_zone[:-1])
            utm_meridian = utm_zone_nr * 6 - 183
            lon_rad = math.radians(lon_dec - utm_meridian)
            lon_tan = math.tan(lon_rad)
            lat_rad = math.radians(lat_dec)
            lat_sin = math.sin(lat_rad)
            grid_convergence = math.degrees(math.atan(lon_tan * lat_sin))
            return grid_convergence

        def approximateIntegral(iterations, x1, x2):
            value = 0

            def f(x):
                return (0.9996 / (math.cos((x-500000) / 6378137)))

            for n in range(1, iterations+1):
                value += f(x1+((n-(1/2))*((x2-x1)/iterations)))
            value2 = ((x2-x1)/iterations)*value
            return value2

        data_fwd = []
        data_bck = []
        data_dist = []
        x1 = refptrow['UTM_east']
        y1 = refptrow['UTM_north']
        # correct for grid convergence on ref pt
        grid_convergence_ref = gridConvergence(
            refptrow['UTM_zone'],
            refptrow['lat_dec'],
            refptrow['lon_dec'])
        for i, row in self.dataframe.iterrows():
            x2 = row['UTM_east']
            y2 = row['UTM_north']
            if x1 == x2:
                same_x = True
            else:
                same_x = False
            # correct for grid convergence on assess pt
            grid_convergence_ass = gridConvergence(
                row['UTM_zone'],
                row['lat_dec'],
                row['lon_dec'])
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
            d_x = approximateIntegral(1000, x1, x2)
            d_y = y2 - y1
            dist = math.sqrt(d_x**2 + d_y**2)
            data_dist.append(dist)
        return (data_fwd, data_bck, data_dist)
