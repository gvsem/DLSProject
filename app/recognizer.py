"""
Recognizer.
"""

from typing import AnyStr, NamedTuple
import torch
import torchvision


class Recognizer:
    """Service recognizes people on image."""

    def __init__(self):
        self.model = torchvision.models.detection\
            .fasterrcnn_resnet50_fpn(pretrained=True)

    def detect_people(self, image, threshold):
        """Detects people on image and returns boxes."""
        model = self.model.eval()
        image = torch\
            .from_numpy(image.copy().astype('float32'))\
            .permute(2, 0, 1) / 255.0
        predictions = model(image[None, ...])
        boxes = predictions[0]['boxes'][
            (predictions[0]['scores'] > threshold)
            & (predictions[0]['labels'] == 1)
        ]
        return boxes.detach().numpy()
