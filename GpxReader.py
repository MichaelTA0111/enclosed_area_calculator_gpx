import gpxpy
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from numpy import arctan2, cos, sin, sqrt, pi, append, diff, deg2rad


class GpxReader:
    """
    Class to read two gpx files: one for the predetermined line and one for the actual line taken
    This class will calculate the the distance of the predetermined line, the area between the route taken,
    and the average deviation from the line
    """

    def __init__(self, gpx_dir, earth_radius=6378137):
        """
        Constructor for the gpx reader
        :param gpx_dir: The file directory for the gpx files to be read
        :param earth_radius: The radius of Earth in metres, which is used for calculations with latitudes
        and longitudes
        """
        self.__gpx_data = []
        self.__segment = []
        self.__lon_lat_line = []
        self.__lon_lat_mission = []
        self.__lon_lat_polygon = []
        self.__lon_polygon = []
        self.__lat_polygon = []
        self.__earth_radius = earth_radius
        self.__line = None
        self.__mission = None
        self.__polygon = None
        self.__area = None
        self.__distance = None
        self.__av_deviation = None
        self.read_segments(gpx_dir)
        self.create_polygons()
        self.calculate_line_distance()
        self.calculate_area()
        self.calculate_av_deviation()

    def read_segments(self, gpx_dir):
        """
        A function to read the latitudes and longitudes from the gpx files for both lines individually
        and combined
        :param gpx_dir: The file directory for the gpx files to be read
        """
        with open(gpx_dir[0]) as fh:  # Open the straight line gpx file
            self.__gpx_data.append(gpxpy.parse(fh))

        with open(gpx_dir[1]) as fh:  # Open the gpx file for the actual route taken
            self.__gpx_data.append(gpxpy.parse(fh))

        for i in range(0, 2):  # Append the segments to the gpx reader object
            self.__segment.append(self.__gpx_data[i].tracks[0].segments[0])

        for coords in self.__segment[0].points:  # Add the lat/long from the straight line
            self.__lon_lat_line.append([coords.longitude, coords.latitude])
            self.__lon_lat_polygon.append([coords.longitude, coords.latitude])

        for coords in self.__segment[0].points[::-1]:  # Add the lat/long from the straight line in reverse order
            # This helps to plot the graphs
            self.__lon_lat_line.append([coords.longitude, coords.latitude])

        for coords in self.__segment[1].points:  # Add the lat/long from the actual line
            self.__lon_lat_mission.append([coords.longitude, coords.latitude])

        for coords in self.__segment[1].points[::-1]:  # Add the lat/long from the actual line in reverse order
            # This helps to plot the graphs
            self.__lon_lat_mission.append([coords.longitude, coords.latitude])
            self.__lon_lat_polygon.append([coords.longitude, coords.latitude])

        for coords in self.__segment[0].points[0:1]:  # Add the first lat/long from the straight line
            # This will close the polygon
            self.__lon_lat_polygon.append([coords.longitude, coords.latitude])

        for ords in self.__lon_lat_polygon:  # Store the lat/long in new arrays
            # This is used to help calculations later
            self.__lon_polygon.append(ords[0])
            self.__lat_polygon.append(ords[1])

    def create_polygons(self):
        """
        Function to create polygons for each of the lines individually and combined
        """
        self.__line = Polygon(self.__lon_lat_line)
        self.__mission = Polygon(self.__lon_lat_mission)
        self.__polygon = Polygon(self.__lon_lat_polygon)

    def calculate_line_distance(self):
        """
        Function to calculate the distance of the straight line using the haversine formula
        """
        # Positions of each end of the straight line
        lat_1 = deg2rad(self.__segment[0].points[0].latitude)
        lat_2 = deg2rad(self.__segment[0].points[-1].latitude)
        lon_1 = deg2rad(self.__segment[0].points[0].longitude)
        lon_2 = deg2rad(self.__segment[0].points[-1].longitude)

        # Difference in the positions of latitude and longitude
        dlon = lon_2 - lon_1
        dlat = lat_2 - lat_1

        # Haversine formula, assumes Earth to be a perfect sphere
        a = sin(dlat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(dlon / 2) ** 2
        c = 2 * arctan2(sqrt(a), sqrt(1 - a))

        # Calculates the distance between the two end points of the straight line
        self.__distance = self.__earth_radius * c

    def calculate_area(self):
        """
        Function to calculate the area enclosed between both lines using the line integral based on
        Green's Theorem, assuming Earth to be a perfect sphere
        Code sourced from
        https://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python
        """
        # Convert all latitudes and longitudes from degrees to radians
        lats = deg2rad(self.__lat_polygon)
        lons = deg2rad(self.__lon_polygon)

        # Close the polygon if it doesn't end at the same point as it started at
        if lats[0] != lats[-1]:
            lats.append(lats[0])
            lons.append(lons[0])

        # Colatitudes relative to (0,0)
        a = sin(lats / 2) ** 2 + cos(lats) * sin(lons / 2) ** 2
        colat = 2 * arctan2(sqrt(a), sqrt(1 - a))

        # Azimuths relative to (0,0)
        az = arctan2(cos(lats) * sin(lons), sin(lats)) % (2 * pi)

        # Calculate diffs
        # daz = diff(az) % (2*pi)
        daz = diff(az)
        daz = (daz + pi) % (2 * pi) - pi

        deltas = diff(colat) / 2
        colat = colat[0:-1] + deltas

        # Perform integral
        integrands = (1 - cos(colat)) * daz

        # Integrate
        area = abs(sum(integrands)) / (4 * pi)

        area = min(area, 1 - area)

        self.__area = area * 4 * pi * self.__earth_radius ** 2  # Store area in square metres

    def calculate_av_deviation(self):
        """
        Function to calculate the average deviation from the line
        """
        self.__av_deviation = self.__area / self.__distance

    def plotter(self, graph_dir):
        """
        Function to plot the graphs of both lines side by side and of both lines combined
        :param graph_dir: The file directories where the graphs should be saved
        """
        plt.plot(*self.__line.exterior.xy, label="Line")
        plt.plot(*self.__mission.exterior.xy, label="Mission")
        plt.grid()
        plt.title('Track')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.savefig(graph_dir[0])
        plt.show()

        plt.plot(*self.__polygon.exterior.xy, label="Joined Lines")
        plt.grid()
        plt.title('Track')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.savefig(graph_dir[1])
        plt.show()

    def get_distance(self):
        """
        Getter for the distance of the straight line
        :return: The distance of the straight line in metres
        """
        return self.__distance

    def get_area(self):
        """
        Getter for the area between the lines
        :return: The area between the lines in square metres
        """
        return self.__area

    def get_av_deviation(self):
        """
        Getter for the average deviation from the straight line
        :return: The average deviation from the straight line in metres
        """
        return self.__av_deviation


def print_statistics(mission):
    """
    Function to print out the statistics calculated about the mission
    :param mission: The mission being analysed
    """
    distance = "{:.2f}".format(mission.get_distance() / 1000.)
    area = "{:.2f}".format(mission.get_area() / 1000000.)
    av_deviation = "{:.1f}".format(mission.get_av_deviation())
    print('The total length of the line was ' + distance + ' km.')
    print('The total area between the line and the route taken was ' + area + ' square km.')
    print('The average deviation from the line was ' + av_deviation + ' metres.')


if __name__ == '__main__':
    print('Please run main.py')
