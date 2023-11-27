# cloud_storage_interface.py
from abc import ABC, abstractmethod


class CloudStorageInterface(ABC):
    @abstractmethod
    def store_dataFrame(self, container_name, file_name, file_format, dataFrame):
        """
        Store a Pandas DataFrame.

        Parameters:
        - container_name: Name of the storage container or bucket.
        - file_name: Name of the file to be stored.
        - file_format: File format for storing the data (either 'excel' or 'csv').
        - dataFrame: Pandas DataFrame to be stored.

        Returns:
        - object_url: URL of the stored object.
        """
        pass

    @abstractmethod
    def retrieve_dataFrame(self, object_url):
        """
        Retrieve a Pandas DataFrame.

        Parameters:
        - object_url: URL of the object to be retrieved.

        Returns:
        - dataFrame: Pandas DataFrame containing the retrieved data.
        """
        pass

    @abstractmethod
    def store_dataFrame_to_sheet(
        self, container_name, file_name, file_format, dataFrame_dict
    ):
        """
        Store multiple Pandas dataFrames in a single file (Excel or CSV) and upload it to cloud provider.

        Parameters:
        - container_name: Name of the storage container or bucket.
        - file_name: Name of the file (without extension).
        - file_format: File format for storing the data ('excel' or 'csv'). Default is 'excel'.
        - dataFrame_dict: Dictionary where keys are sheet names and values are Pandas dataFrames.

        Returns:
        - object_url: URL of the stored object
        """
        pass

    @abstractmethod
    def retrieve_dataFrames_from_sheets(self, container_name, file_key, file_format):
        """
        Retrieve Pandas dataFrames from a file stored.

        Parameters:
        - container_name: Name of the storage container or bucket.
        - file_key: Key of the file.
        - file_format: File format for storing the data ('excel' or 'csv'). Default is 'excel'.

        Returns:
        - dataFrames: Dictionary where keys are sheet names and values are Pandas dataFrames.
        """
        pass
