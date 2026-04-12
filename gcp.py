from google.cloud import storage
import pandas as pd
from io import StringIO
from google.api_core.exceptions import Conflict

def get_file_from_bucket(bucket_name: str, file_path: str) -> pd.DataFrame:
    '''
    imports csv file from GCP and returns as a dataframe
    '''
    client = storage.Client()

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    csv_text = blob.download_as_text()

    df = pd.read_csv(StringIO(csv_text))

    return df

def write_df_to_bucket(bucket_name: str, file_path: str, df: pd.DataFrame) -> None:
    '''
    Writes a dataframe to a bucket in GCP
    '''
    client = storage.Client()

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
    
    return

def create_bucket(bucket_name: str, project_id: str) -> None:
    '''
    attempts to create a bucket. skips if bucket already exists
    '''
    client = storage.Client(project=project_id)

    try:
        client.create_bucket(bucket_name)

    except Conflict:
        pass