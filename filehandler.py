import pandas
import utm

class Source():
    def __init__(self, file):
        data = pandas.read_csv(file)
        self.coords = []
        for entry,row in data.iterrows():
            lat_sign = 1
            lon_sign = 1
            if row['Lat Dir'] == 'S':
                lat_sign = -1
            if row['Lon Dir'] == 'W':
                lon_sign = -1
            lat = (row['Lat Deg'] + row['Lat Min']/60 + row['Lat Sec']/3600) * lat_sign
            lon = (row['Lon Deg'] + row['Lon Min']/60 + row['Lon Sec']/3600) * lon_sign
            utm_coords = utm.project((lon,lat))
            coord = {
                "id": row['ID'],
                "lat_deg": row['Lat Deg'],
                "lat_min": row['Lat Min'],
                "lat_sec": row['Lat Sec'],
                "lat_dir": row['Lat Dir'],
                "lon_deg": row['Lon Deg'],
                "lon_min": row['Lon Min'],
                "lon_sec": row['Lon Sec'],
                "lon_dir": row['Lon Dir'],
                "lat_dec": lat,
                "lon_dec": lon,
                "UTM_zone": str(utm_coords[0]) + utm_coords[1],
                "UTM_east": utm_coords[2],
                "UTM_north": utm_coords[3],
                }
            self.coords.append(coord)

    def filterData(self,field,items):
        new_coords = []
        for point in self.coords:
            if point[field] in items:
                new_coords.append(point)
        self.coords = new_coords

def write_csv(filename, dataframe):
    new_file = filename.split('.')[0]+"_output.csv"
    dataframe.to_csv(new_file)
