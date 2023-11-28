import pandas as pd
import boto3
from botocore.exceptions import ClientError
from io import BytesIO, StringIO
from app.cloud_storage.cloud_storage_interface import CloudStorageInterface


class S3Manager(CloudStorageInterface):
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.region_name = region_name

    def store_dataFrame(self, container_name, file_name, file_format, dataFrame):
        """
        Store a Pandas DataFrame in AWS S3.

        Parameters:
        - container_name: Name of the S3 bucket.
        - file_format: File format for storing the data (either 'excel' or 'csv').
        - file_name: Name of the file to be stored in S3.
        - dataFrame: Pandas DataFrame to be stored.

        Returns:
        - object_url: URL of the stored object in S3.
        """
        if file_format not in ["excel", "csv"]:
            raise ValueError(
                "Invalid file format. Supported formats are 'excel' or 'csv."
            )
        if file_format == "excel":
            buffer = BytesIO()
            dataFrame.to_excel(buffer, index=False)
            file_extension = "xlsx"
        else:  # csv
            buffer = StringIO()
            dataFrame.to_csv(buffer, index=False)
            file_extension = "csv"

        # Upload the data to S3
        s3_key = f"{file_name}.{file_extension}"
        self.s3_client.put_object(
            Body=buffer.getvalue(), Bucket=container_name, Key=s3_key
        )

        # Get the object URL
        return f"https://s3.amazonaws.com/{container_name}/{s3_key}"

    def retrieve_dataFrame(self, object_url):
        """
        Retrieve a Pandas DataFrame from the given S3 object URL.

        Parameters:
        - object_url: URL of the object to be retrieved from S3.

        Returns:
        - dataFrame: Pandas DataFrame containing the retrieved data.
        """
        # Parse the S3 URL to get bucket and key
        _, _, _, bucket, key = object_url.split("/", 4)

        # Retrieve the object from S3
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read()

        # Convert content to DataFrame based on file format
        if key.endswith(".csv"):
            dataFrame = pd.read_csv(BytesIO(content))
        elif key.endswith(".xlsx"):
            dataFrame = pd.read_excel(BytesIO(content))
        else:
            raise ValueError(
                "Unsupported file format. Supported formats are 'csv' and 'xlsx'."
            )

        return dataFrame

    def store_dataFrame_to_sheet(
        self, container_name, file_name, file_format, dataFrame_dict
    ):
        """
        Store multiple Pandas dataFrames in a single file (Excel or CSV) and upload it to S3.

        Parameters:
        - container_name: Name of the S3 bucket.
        - file_name: Name of the file
        - file_format: File format for storing the data ('excel' or 'csv')
        - dataFrame_dict: Dictionary where keys are sheet names and values are Pandas dataFrames.

        Returns:
        - object_url: URL of the stored object in S3.
        """
        # Create an in-memory buffer for the file
        file_buffer = BytesIO()

        if file_format == "excel":
            # Use ExcelWriter for multiple sheets
            with pd.ExcelWriter(file_buffer, engine="xlsxwriter") as writer:
                for sheet_name, dataFrame in dataFrame_dict.items():
                    dataFrame.to_excel(writer, sheet_name=sheet_name, index=False)
            file_extension = "xlsx"
        elif file_format == "csv":
            # Use StringIO for CSV
            for sheet_name, dataFrame in dataFrame_dict.items():
                csv_content = dataFrame.to_csv(index=False)
                file_buffer.write(csv_content.encode())
            file_extension = "csv"
        else:
            raise ValueError(
                "Invalid file format. Supported formats are 'excel' or 'csv'."
            )

        # Reset the buffer's position to the beginning
        file_buffer.seek(0)

        # Upload the file to S3
        file_key = f"{file_name}.{file_extension}"
        self.s3_client.put_object(
            Body=file_buffer.getvalue(), Bucket=container_name, Key=file_key
        )

        return (
            f"https://{container_name}.s3.{self.region_name}.amazonaws.com/{file_key}"
        )

    def retrieve_dataFrames_from_sheets(
        self, file_key, container_name, file_format="excel"
    ):
        """
        Retrieve Pandas dataFrames from a file stored in S3.

        Parameters:
        - file_key: Key of the file in S3.
        - container_name: Name of the AWS S3 bucket.
        - file_format: File format for storing the data ('excel' or 'csv'). Default is 'excel'.

        Returns:
        - dataFrames: Dictionary where keys are sheet names and values are Pandas dataFrames.
        """
        # Download the file from S3
        try:
            response = self.s3_client.get_object(Bucket=container_name, Key=file_key)
            file_content = response["Body"].read()

            # Read the file into Pandas dataFrames based on the file format
            sheet_data = []
            if file_format == "excel":
                with pd.ExcelFile(BytesIO(file_content)) as xls:
                    sheet_data.extend(
                        (sheet_name, pd.read_excel(xls, sheet_name))
                        for sheet_name in xls.sheet_names
                    )
            elif file_format == "csv":
                sheet_data.append((file_key, pd.read_csv(BytesIO(file_content))))
            else:
                raise ValueError("Invalid file format. Supported formats are 'excel' or 'csv'.")

            return sheet_data
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise ValueError(
                    f"The specified key '{file_key}' does not exist in the S3 bucket"
                ) from e
            else:
                print(f"Error retrieving file from S3: {e}")
            return []
