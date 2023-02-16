import csv
from typing import Sequence
import numpy as np
from types import SimpleNamespace
from typing import Union
from pathlib import Path
import xmltodict
import types
import gzip
import shutil

POLY_ACTIVATE = True
try:
    import polyscope as ps

    # Should be run only once
    # Set up direction
    ps.init()
    ps.set_up_dir("z_up")
except:
    print("POLYSCOPE IS NOT WORKING")
    print("This is normal for colab")
    POLY_ACTIVATE = False


class Arc_reader():
    def __init__(self, name="pointcloud"):
        """
        Class reading the csv extract of an ARC file.
        To use this class, create an object then use the load_csv function to load in raw_data all csv data.
        Process the raw_data with get_coordinate and get_point_cloud_data to access them
        from self.coordinate and self.data.
        Arg
        :param name: Name use on the polyscope visualisation
        """
        self.raw_data = SimpleNamespace()
        self.data = SimpleNamespace()
        self.coordinate = np.empty([1, 3])
        self.name = name
        self.name_file = ""
        self.arc_type = ""
        self.metaparameters = types.SimpleNamespace()
        self.attribute_to_load = list()  # List of the parameters to load on display. Empty = all data will be displayed
        self.edge_index = [[], []]  # Source and destination

        self.__SECTIONS_NAMES = ["Connectivity (nb, type, nb of nodes)", "Coordinates (nb)",
                                 "Post value (name, number)"]

    def load_csv(self, file: Union[str, Path], attribute_to_load: list = None) -> None:
        """Load ARC files csv values to raw_data
        :param file: Path to the UNV file converted into csv to load
        :param attribute_to_load: list of the parameters to load, if none, all is loaded
        :return: None
        """
        file = Path(file)
        self.name_file = file.name
        self.path_file = file
        self.arc_type = self._get_arc_type(file.name)

        # If a filter is defined; the connectivity and coordinates must be loaded
        if attribute_to_load is not None:
            for to_be_in in ["Connectivity", "Coordinates"]:
                if not to_be_in in attribute_to_load:
                    attribute_to_load.append(to_be_in)

        self.attribute_to_load = attribute_to_load

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
                    if attribute_to_load is None:
                        getattr(self.raw_data, last_attribute).add_values(row)
                    elif last_attribute in attribute_to_load:
                        getattr(self.raw_data, last_attribute).add_values(row)

    def _get_arc_type(self, file_name: Union[str, Path]) -> str:
        """
        Extract the type of the part. This can be a part, a supports or a baseplate.
        :param file_name: name of the arc file containing the type of part
        :return: str, type of file
        """
        file_name = str(file_name)

        if "baseplate" in file_name:
            return "baseplate"
        elif "part" in file_name:
            return "part"
        elif "supports" in file_name:
            return "supports"
        else:
            return None

    def get_coordinate(self):
        """Extract the coordinate from the raw data and create a numpy array with them"""
        try:
            self.coordinate = np.zeros([int(self.raw_data.Coordinates.nb), 3])
        except:
            print("raw_data not found, please load csv file before with load_csv()")

        for coor in self.raw_data.Coordinates.values:
            id = int(coor[0])
            pos = np.array(coor[1:], dtype=np.float32)
            self.coordinate[id] = pos

    def get_connectivity(self) -> None:
        """Extract the connectivity from the raw data and create a numpy array with them"""
        try:
            self.connectivity = np.zeros([int(self.raw_data.Coordinates.nb), 8])
        except:
            print("raw_data not found, please load csv file before with load_csv()")

        for i, coon in enumerate(self.raw_data.Connectivity.values):
            id = i  # int(coon[0]) # Extract the id of the node
            neigh = np.array(coon[1:], dtype=np.int32)  # Extract the neighbors
            self.connectivity[id] = neigh

    def add_id(self) -> None:
        """Add an ID features to all nodes, the ID is equal to the nodes positions in the nodes list"""
        if POLY_ACTIVATE:
            self.ps_net.add_scalar_quantity("ID", np.arange(0, self.coordinate.shape[0]), enabled=True, cmap="jet")
        else:
            print("Polyscope is deactivated, so no id will be displayed")

    @staticmethod
    def clean_data(data) -> np.ndarray:
        """Clean data"""
        data = np.asarray(data)
        data = np.squeeze(data)
        return data

    def get_point_cloud_data(self) -> None:
        """Create a point cloud with all the available data."""
        to_avoid = ["Coordinates", "Connectivity"]

        for raw in dir(self.raw_data):
            # Iterate on the raw_data
            # We do not want to process hidden data (__XXX), Coordinates, Connectivity and
            # data not in the filter (attribute_to_load) if it is defined
            process_this_loop = True
            if raw[0:2] == "__" or raw in to_avoid:
                process_this_loop = False
                # not processing on the class private attribute
            elif not self.attribute_to_load is None:
                # If we have to only process selected data
                if raw in self.attribute_to_load:
                    # And we are now having the data that we area asked to process
                    process_this_loop = True
                else:
                    # We do not want to process those data
                    process_this_loop = False

            if process_this_loop:
                setattr(self.data, raw, self.clean_data(getattr(self.raw_data, raw).values[4:]))


    def load_meta_parameters(self, increment_id: int, build_path: Path = None, increments_path: Path = None) -> None:
        """
        Automaticaly load the xml files containing the build parameters and the layers times.
        This function must be run AFTER load_csv
        :arg
            build_path: Where is the build.xml file. If None, default value will be created
            increments_path: Where the increment.xml file is. If None, default value will be created
            increment_id: Step of the simulation iteration (not equal to the name of the arc folder).
        :return: None
        """
        process_folder = Path(self.path_file).parents[2]  # Extract the Process folder where are stored the information
        process_step = int(Path(self.path_file).parents[0].name)
        self.metaparameters.process_step = process_step

        # Generate default values if needed:
        if build_path is None:
            build_path = process_folder / r"Stages" / "Build.xml"
        if increments_path is None:
            increments_path = process_folder / r"_Results_" / "Meta" / "Increments.xml"

        # Load the build information with the main printing parameters
        with open(build_path) as f:
            build = xmltodict.parse(f.read())

            self.metaparameters.speed_m_s = float(
                build["stageInfoFile"]["stage"]["stageType"]["standardParameter"]["speed"]["#text"])
            self.metaparameters.layerThickness_m = float(
                build["stageInfoFile"]["stage"]["stageType"]["standardParameter"]["layerThickness"]["#text"])
            self.metaparameters.power_W = float(
                build["stageInfoFile"]["stage"]["stageType"]["standardParameter"]["power"]["#text"])
            self.metaparameters.initialTemperature_C = float(
                build["stageInfoFile"]["stage"]["stageType"]["thermalParameter"]["initialTemperature"]["#text"])

        # Load the time of each layers
        if not increments_path.exists():
            # If the gz file was not unzip, unzip it
            self.unzip_file( increments_path.parent / (increments_path.name + ".gz"), increments_path)

        with open(increments_path) as f:
            incrememts = xmltodict.parse(f.read())
            self.metaparameters.time_steps_s = float(incrememts['Increments']["Increment"][increment_id]["Time"])
            self.metaparameters.time_steps_length_s = float(
                incrememts['Increments']["Increment"][increment_id]["TimeStepLengthUsed"])
            self.metaparameters.subProcessName = str(
                incrememts['Increments']["Increment"][increment_id]["SubProcessName"])

    def unzip_file(self, file_in: Path, file_out: Path) -> None:
        """Unzip a file.

        Unzip a file and save it in the save folder.

        """
        with gzip.open(file_in, "rb") as f_in:
            with open(file_out, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def get_edge_index(self) -> list:
        """Compute the edges index of the part.
        The used format will be the one of pytorch geometric, 2 lists, one with sources nodes qnd the other with
        destination nodes."""

        for neighbor in self.connectivity:
            # A neighbor is a set of 8 nodes.
            for source in neighbor:
                for destination in neighbor:
                    if source == destination:
                        pass
                    else:
                        # -1 as our vertices id start at 0, but not the one in Simufact who start at 1
                        self.__add_edge(source - 1, destination - 1)

        # Remove duplicate
        self.edge_index = np.unique(np.array(self.edge_index), axis=1).tolist()

        return self.edge_index

    def add_edge(self, source: int, destination: int) -> None:
        """
        Add an edges to the self.edge_index
        :param source: source nodes
        :param destination: destination node
        :return:
        """
        self.__add_edge(source, destination)

    def __add_edge(self, source: int, destination: int) -> None:
        """
        Add an edges to the self.edge_index
        :param source: source nodes
        :param destination: destination node
        :return:
        """
        source = int(source)
        destination = int(destination)
        self.edge_index[0].append(source)
        self.edge_index[1].append(destination)

    def display(self, edges_radius: float = 0.002):
        """Generate a curve network representation of the data with polyscope
        :param edges_radius: size of the edges
        """
        if not POLY_ACTIVATE:
            raise("ERROR polyscope is deactivated")

        # Define the graph
        self.ps_net = ps.register_curve_network(self.name, self.coordinate, np.array(self.edge_index).T,
                                                radius=edges_radius)

        # Add id
        self.add_id()

        # Create vectors:
        # Deformation vectors
        if hasattr( self.data, "XDIS") and hasattr( self.data, "YDIS") and hasattr( self.data, "ZDIS"):
            displacement_vectors = np.vstack((self.data.XDIS, self.data.YDIS, self.data.ZDIS)).T
            self.ps_net.add_vector_quantity("Deformation vectors", displacement_vectors)

        # Add all available scalar values
        for data in dir(self.data):
            if data[0:2] == "__":
                pass
            else:
                self.ps_net.add_scalar_quantity(data, getattr(self.data, data), cmap="jet")




class Content():
    def __init__(self, name=None):
        self.values = []
        self.name = name

        # define who is using float value and who is using int value
        # self.__TO_FLOAT = ["Coordinates", 'XDIS', 'YDIS', 'ZDIS', "ARCDISX", "ARCDISY", "ARCDISZ", "SOLIDFRA", "AM-ZDISP"]
        self.__TO_INT = ["Connectivity", "GLUE", "NDDM", "ELERROR", "EXPRSS"]

    def add_values(self, val):
        """Add a values to the list of values"""
        if self.name in self.__TO_INT:
            self.values.append([int(v) for v in val])
        else:
            self.values.append([float(v) for v in val])

    def add_information(self, titles: Sequence[str], data: Sequence[str]):
        """Add the information attribute to self"""
        for title, atr in zip(titles, data):
            setattr(self, title, atr)
