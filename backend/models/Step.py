# backend/models/Step.py
from dataclasses import dataclass


@dataclass
class Step:
    def __init__(self):
        self.gcs_bucket_name = ""
        self.table_name = ""
        self.source_tables = []
        self.is_master_table = False

    def add_gcs_bucket_name(self, gcs_bucket_name):
        self.gcs_bucket_name = gcs_bucket_name

    def add_table_name(self, table_name):
        self.table_name = table_name

    def add_de_table(self, de_table_name):
        self.source_tables.append(de_table_name)

    def remove_de_table(self, de_table_name):
        self.source_tables.remove(de_table_name)

    def get_all_de_tables(self):
        return self.source_tables

    def update_de_table(self, table_name, de_table_name):
        index = self.source_tables.index(table_name)
        self.source_tables[index] = de_table_name

    def delete_de_table(self, table_name):
        index = self.source_tables.index(table_name)
        self.source_tables.pop(index)

    def is_master(self):
        self.is_master_table = True

    def __repr__(self):
        return f"Step(gcs_bucket_name={self.gcs_bucket_name}, table_name={self.table_name}, source_tables={self.source_tables})"

    def to_dict(self):
        return {
            'gcs_bucket_name': self.gcs_bucket_name,
            'table_name': self.table_name,
            'source_tables': self.source_tables
        }
