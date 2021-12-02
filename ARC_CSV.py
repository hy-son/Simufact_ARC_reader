import csv
from typing import Sequence
import numpy as np
from types import SimpleNamespace
import polyscope as ps

# Should be run only once
# Set up direction
ps.init()
ps.set_up_dir("z_up")

class Arc_reader():
    def __init__(self):
        self.raw_data = SimpleNamespace()
        self.data = SimpleNamespace()
        self.coordinate = np.empty([1,3])

        self.__SECTIONS_NAMES = ["Connectivity (nb, type, nb of nodes)", "Coordinates (nb)", "Post value (name, number)"]

    def load_csv(self, file: str):
        """Load ARC files csv values to raw_data"""
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            last_attribute = None

            for row in csv_reader:
                # row is a list
                # If this is information on the object
                if row[0] in self.__SECTIONS_NAMES:
                    # Add the section to the object
                    if row[0] == "Post value (name, number)":
                        last_attribute = row[1]
                    else:
                        last_attribute = row[0]

                    # Extract information title:
                    info_titles = row[0].split("(")[1].split(")")[0].split(",")
                    info_value = row[1:]

                    # Create a callable name for the attibute
                    last_attribute = last_attribute.split(" (")[0].replace(" ", "_")

                    # Add to the Arc object a Content object
                    setattr(self.raw_data, last_attribute, Content(last_attribute))
                    getattr(self.raw_data, last_attribute).add_information(titles=info_titles, data=info_value)

                else:
                    # Add the data to their attribute
                    getattr(self.raw_data, last_attribute).add_values(row)

    def get_coordinate(self):
        """Extract the coordinate from the raw data and create a numpy array with them"""
        try:
            self.coordinate = np.zeros([int(self.raw_data.Coordinates.nb),3])
        except:
            print("raw_data not found, please load csv file before with load_csv()")

        for coor in self.raw_data.Coordinates.values:
            id = int(coor[0])
            pos = np.array(coor[1:], dtype=float)
            self.coordinate[id] = pos

    @staticmethod
    def clean_data(data):
        """Clean data"""
        data = np.asarray(data)
        data = np.squeeze(data)
        return data

    def get_point_cloud_data(self):
        """Create a point cloud with all the available data"""
        ps.register_point_cloud("pointscloud", self.coordinate)
        to_avoid = ["Coordinates", "Connectivity"]

        for raw in dir(self.raw_data):
            # Iterate on the raw_data
            if raw[0:2] == "__" or raw in to_avoid:
                pass
                # but not on the class private attribute
            else:
                setattr(self.data, raw, self.clean_data(getattr(self.raw_data, raw).values[4:]))
                ps.get_point_cloud("pointscloud").add_scalar_quantity(
                    getattr(self.raw_data, raw).name, getattr(self.data, raw), cmap="jet")

class Content():
    def __init__(self, name=None):
        self.values = []
        self.name = name

        # define who is using float value and who is using int value
        #self.__TO_FLOAT = ["Coordinates", 'XDIS', 'YDIS', 'ZDIS', "ARCDISX", "ARCDISY", "ARCDISZ", "SOLIDFRA", "AM-ZDISP"]
        self.__TO_INT = ["Connectivity", "GLUE", "NDDM", "ELERROR", "EXPRSS" ]
    def add_values(self, val):
        """Add a values to the list of values"""
        if self.name in self.__TO_INT:
            self.values.append([int(v) for v in val])
        else:
            self.values.append([float(v) for v in val])

    def add_information(self,  titles: Sequence[str], data: Sequence[str]):
        """Add the information attribute to self"""
        for title, atr in zip(titles, data):
            setattr(self, title, atr)