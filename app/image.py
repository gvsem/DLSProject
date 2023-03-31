"""
Image.
"""

from typing import Tuple
import cv2
import numpy


class Image:
    """Class represents a mutable image"""

    def __init__(self, content: str) -> None:
        """Ctor."""
        self.content = content

    def draw_rect(
            self,
            box: Tuple[int, int, int, int],
            color: Tuple[int, int, int]
    ) -> None:
        """Draws a rect with given 'box' and color on this image."""
        self.content = cv2.rectangle(
            numpy.array(self.content),
            (int(box[0]), int(box[1])),
            (int(box[2]), int(box[3])),
            (color[2], color[1], color[0]),
            2
        )

    def save_as(self, filepath: str):
        """Saves image to file."""
        cv2.imwrite(filepath, self.content)

    @staticmethod
    def load(imagepath: str) -> 'Image':
        """Loads image of given path to cv2 object."""
        return Image(cv2.imread(imagepath))
