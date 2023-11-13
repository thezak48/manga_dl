"""File handler module."""
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile


class FileHandler:
    """
    A class to handle file operations.

    This class provides methods to create a ComicInfo.xml file,
    create a .cbz file from a directory, and cleanup a directory.

    Attributes:
        logger: An instance of log.Logger for log.
    """

    def __init__(self, logger):
        self.logger = logger

    def create_comic_info(self, series, genres, summary, language_iso="en"):
        """
        Create a ComicInfo.xml file for the .cbz file.
        """
        root = ET.Element("ComicInfo")
        ET.SubElement(root, "Series").text = series
        ET.SubElement(root, "Genre").text = ", ".join(genres)
        ET.SubElement(root, "Summary").text = summary
        ET.SubElement(root, "LanguageISO").text = language_iso

        tree = ET.ElementTree(root)
        tree.write("ComicInfo.xml", encoding="utf-8", xml_declaration=True)
        self.logger.info("ComicInfo.xml for %s created", series)

    def make_cbz(self, directory_path, compelte_dir, output_path):
        """
        Create a .cbz file from a directory.
        """
        if not os.listdir(directory_path):
            self.logger.warning("No files found in %s", directory_path)
            return

        output_path = os.path.join(
            compelte_dir, f"{os.path.basename(directory_path)}.cbz"
        )
        zipf = zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED)

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file), os.path.basename(os.path.join(root, file))
                )
                self.logger.info("%s added to %s", file, output_path)

        zipf.write("ComicInfo.xml", "ComicInfo.xml")
        self.logger.info("ComicInfo.xml added to %s", output_path)

        zipf.close()

    def cleanup(self, directory_path):
        """
        Cleanup a directory.
        """
        shutil.rmtree(directory_path)
        self.logger.info("Cleaned up %s", directory_path)
