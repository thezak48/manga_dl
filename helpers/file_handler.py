"""File handler module."""
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from helpers.logging import setup_logging


class FileHandler:
    """
    A class to handle file operations.

    This class provides methods to create a ComicInfo.xml file,
    create a .cbz file from a directory, and cleanup a directory.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    def __init__(self):
        self.logger = setup_logging()

    def create_comic_info(self, series, genres, summary, language_iso="en"):
        """
        Create a ComicInfo.xml file for the .cbz file.
        """
        # Create XML elements
        root = ET.Element("ComicInfo")
        ET.SubElement(root, "Series").text = series
        ET.SubElement(root, "Genre").text = ", ".join(genres)
        ET.SubElement(root, "Summary").text = summary
        ET.SubElement(root, "LanguageISO").text = language_iso

        # Create XML tree and write to file
        tree = ET.ElementTree(root)
        tree.write("ComicInfo.xml", encoding="utf-8", xml_declaration=True)

    def make_cbz(self, directory_path, compelte_dir, output_path):
        """
        Create a .cbz file from a directory.
        """
        output_path = os.path.join(
            compelte_dir, f"{os.path.basename(directory_path)}.cbz"
        )
        zipf = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file), os.path.basename(os.path.join(root, file))
                )

        zipf.write("ComicInfo.xml", "ComicInfo.xml")

        zipf.close()

    def cleanup(self, directory_path):
        """
        Cleanup a directory.
        """
        shutil.rmtree(directory_path)
