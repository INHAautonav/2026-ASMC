import json
import os
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt
from shapely import affinity
from shapely.geometry import Polygon, box


class MoraiMap:
    """
    MoraiMap database class for extracting
    geometric information from mgeo data.
    """

    def __init__(self, data_root: str = "/data/morai", map_name: str = "Yongin_Track") -> None:
        """
        Load the layers and initalize map database.
        :param data_root: Path to the morai data
        :param map_name: Name of the map to load.
                         Available maps are `Sangam Track`.
        """
        super().__init__()
        assert map_name in os.listdir(data_root), f"Unknown map name {map_name}!"

        self.data_path = os.path.join(data_root, map_name)
        self.map_name = map_name

        self.drivable_area = self._load_layer("road_mesh_out_line.json")
        self.link_set = self._load_layer("link_set.json")

    def _load_layer(self, json_file: str) -> dict:
        """
        Load the layer from json and return the dictionary
        indexed by token of each component of the layer.
        :param json_file: Path of json file.
        :return: Dict of components corresponding to a layer.
        """
        json_file = os.path.join(self.data_path, json_file)
        with open(json_file, "r") as f:
            layer = json.load(f)

        layer_dict = dict()
        for component in layer:
            idx = component.pop("idx")
            layer_dict[idx] = component

        return layer_dict

    def extract_polygon(self, layer: str, idx: str) -> Polygon:
        """
        Extract the polygon of `drivable_area` and `crosswalk`.
        :param layer: Name of the layer.
        :param idx: Token of the component.
        :return: Polygon instance.
        """
        assert layer in [
            "drivable_area",
        ], "Layer name must be 'drivable_area'!"

        if layer == "drivable_area":
            exterior = self.drivable_area[idx]["points"]
            interior = [poly["points"] for poly in self.drivable_area[idx]["interiors"]]

        return Polygon(exterior, interior)

    def visualize_track(self):
        """
        Visualize the track using matplotlib.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        for idx in self.drivable_area:
            polygon = self.extract_polygon("drivable_area", idx)
            x, y = polygon.exterior.xy
            ax.plot(x, y, color="black", linewidth=1.0)
            
            for interior in polygon.interiors:
                x, y = interior.xy
                ax.plot(x, y, color="black", linewidth=1.0)

        for idx in self.link_set:
            points = np.array(self.link_set[idx]["points"])
            ax.plot(points[:, 0], points[:, 1], color="red", linewidth=1.0)

        ax.set_aspect("equal")
        plt.show()
 
    @staticmethod
    def get_patch_coord(patch_box: Tuple[float, float, float, float], patch_angle: float = 0.0) -> Polygon:
        """
        Convert patch_box to shapely Polygon coordinates.
        :param patch_box: Patch box defined as [x_center, y_center, height, width].
        :param patch_angle: Patch orientation in degrees.
        :return: Box Polygon for patch_box.
        """
        patch_x, patch_y, patch_h, patch_w = patch_box

        x_min = patch_x - patch_w / 2.0
        y_min = patch_y - patch_h / 2.0
        x_max = patch_x + patch_w / 2.0
        y_max = patch_y + patch_h / 2.0

        patch = box(x_min, y_min, x_max, y_max)
        patch = affinity.rotate(patch, patch_angle, origin=(patch_x, patch_y), use_radians=False)

        return patch
