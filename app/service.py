"""
Backend Services: FileService.
"""

import os
import base64
from typing import AnyStr, NamedTuple, Tuple
from werkzeug.utils import secure_filename
from .image import Image
from .recognizer import Recognizer


class FileExplorer:
    """Class manages files on this backend."""

    class Config(NamedTuple):
        """Configuration for File Service."""
        dir_root: str
        dir_static: str
        dir_upload: str

    def __init__(self, config: Config) -> None:
        """Contructor."""
        self.attr = config

    def relative(self, directory: str, filename: str) -> str:
        """Returns '{dir_root}/{directory}/{filename}'."""
        return os.path.join(self.attr.dir_root, directory, filename)

    def relative_upload(self, filename: str) -> str:
        """Returns path of file relative to upload folder."""
        return os.path.join(self.attr.dir_upload, filename)

    def relative_static(self, filename: str) -> str:
        """Returns path of file relative to upload folder."""
        return os.path.join(self.attr.dir_static, filename)

    def static_content(self, filepath: str) -> AnyStr:
        """Returns file with given name in 'static' folder"""
        return self.content_of(self.relative_static(filepath))

    def upload_file(self, file) -> str:
        """
        Uploads given flask file from 'request.files' 
        and returns filepath for service user.
        """
        filename = secure_filename(file.filename)
        filepath = self.relative_upload(filename)
        file.save(filepath)
        return filepath

    def content_of(self, filepath: str, encoding='UTF-8') -> AnyStr:
        """Reads file content."""
        with open(self.relative('.', filepath), 'r', encoding=encoding) as file:
            return file.read()

    def content_of_binary(self, filepath: str) -> AnyStr:
        """Reads binary file content in base64."""
        with open(self.relative('.', filepath), 'rb') as file:
            return base64.b64encode(file.read())


class Detector:
    """Detection Service."""

    def __init__(self, explorer: FileExplorer, recongizer: Recognizer):
        self.explorer = explorer
        self.recongizer = recongizer

    def process_image(
        self,
        sourcepath: str,
        resultpath: str,
        threshold: str,
        color: Tuple[int, int, int]
    ):
        """Takes image, detects people on it, and saves it with boxes."""
        image = Image.load(sourcepath)
        boxes = self.recongizer.detect_people(image.content, threshold)
        for box in boxes:
            image.draw_rect(box, color)
        image.save_as(resultpath)
