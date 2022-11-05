from io import StringIO, BytesIO
import urllib.request
import urllib.parse
from datetime import datetime
import pickle

import pandas as pd
from azure.storage.blob import BlobClient

from config import Config as cfg


class BlobTable:
    def __init__(self, table_name="", ftype="csv"):
        self.table_name = table_name
        self.ftype = ftype
        self.dfs = {}
    
    @property
    def df(self):
        return pd.concat(self.dfs.values())

    def get_path(self, partition):
        path = "/".join([el for el in [self.table_name, partition] if el])
        return f"{path}.{self.ftype}"

    def download(self, partitions=[], concat=False, **kwargs):
        for p in partitions:
            self.dfs[p] = self.read(p, **kwargs)
            print(datetime.now(), f"read: {self.get_path(p)}", self)

        return self.dfs if not concat else self.df

    def upload(self, dfs):
        for p, df in dfs.items():
            self.write(p, df)
            print(datetime.now(), f"write: {self.get_path(p)}", self)

        return self


class AzureBlobTable(BlobTable):
    def __init__(self, table_name="", ftype="csv"):
        super().__init__(table_name, ftype)
        self.connection_string = cfg.AZURE_CONNECTION_STRING
        self.container_name = cfg.AZURE_CONTAINER_NAME

    @property
    def read(self):
        return {"csv": self.read_csv,
                "parquet": self.read_parquet,
                "pkl": self.read_pkl}[self.ftype]

    @property
    def write(self):
        return {"csv": self.write_csv,
                "parquet": self.write_parquet,
                "pkl": self.write_pkl}[self.ftype]

    def write_csv(self, partition, data):
        client = self.get_client(partition)
        stream = StringIO()
        data.to_csv(stream, index=False)
        client.upload_blob(BytesIO(stream.getvalue().encode("UTF-8")), overwrite=True)

    def read_csv(self, partition):
        client = self.get_client(partition)
        return pd.read_csv(StringIO(client.download_blob().content_as_text()))

    def write_parquet(self, partition, data):
        client = self.get_client(partition)
        stream = BytesIO()
        data.to_parquet(stream, index=False)
        client.upload_blob(data=stream.getvalue(), overwrite=True)

    def read_parquet(self, partition):
        client = self.get_client(partition)
        stream = BytesIO()
        client.download_blob().readinto(stream)
        return pd.read_parquet(stream)

    def write_pkl(self, partition, data):
        client = self.get_client(partition)
        stream = BytesIO()
        pickle.dump(data, stream)
        stream.seek(0)
        client.upload_blob(stream, overwrite=True)

    def read_pkl(self, partition):
        client = self.get_client(partition)
        downloader = client.download_blob(0)
        return pickle.loads(downloader.readall())

    def get_client(self, partition):
        return BlobClient.from_connection_string(conn_str=self.connection_string,
                                                 container_name=self.container_name,
                                                 blob_name=self.get_path(partition))


class ExternalBlobTable(BlobTable):
    def __init__(self, table_name=""):
        super().__init__(table_name, "csv")
        self.url = cfg.FOOTBALL_DATA_URL

    def get_link(self, partition):
        return f"{self.url}/{self.get_path(partition)}"

    def read(self, partition):
        link = self.get_link(partition)
        data = urllib.parse.urlencode({}, doseq=True).encode()
        req = urllib.request.Request(link, data=data, headers={})
        res = urllib.request.urlopen(req).read()

        return pd.read_csv(StringIO(res.decode("utf-8")))
