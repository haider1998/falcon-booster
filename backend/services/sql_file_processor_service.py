# backend/services/sql_file_processor_service.py
import logging
import os
import re

import sqlparse

from backend.config.logging_config import configure_logging
from backend.models.Step import Step
from backend.models.Steps import Steps
from backend.repositories.data_store import DataStore
from backend.services.file_service import FileService
from backend.services.suffix_determiner import SuffixDeterminer

# Configure logging
configure_logging()

data_store = DataStore()


class SQLFileProcessor:
    # Identify the last data loader file
    last_data_loader_index = -1

    def __init__(self, app_name, feed_name, initials_6char):
        self.app_name = app_name
        self.feed_name = feed_name
        self.initials_6char = initials_6char
        self.steps = Steps()
        self.staging_table_dict = {}
        self.suffix_determiner = SuffixDeterminer(app_name, feed_name, initials_6char)
        self.dfa_feed_repo_name = f"50884_{app_name.lower().replace('gcp', 'dfa').replace('-', '_')}_{feed_name.lower().replace('-', '_')}"
        self.file_service = FileService(f'tmp/resource/{self.dfa_feed_repo_name}/scripts/sql', '', '', '', '', '',
                                        '', '', '', False)

    def process_sql_files(self, folder_path_sql):
        logging.info("Feed Respository Name: " + self.dfa_feed_repo_name)
        count_file = 0
        filenames = [f for f in os.listdir(folder_path_sql) if f.endswith('.sql') or f.endswith('.SQL')]

        for i, filename in enumerate(filenames):
            if 'loader' in filename.lower():
                if 'history' not in filename.lower() and 'reference' not in filename.lower() and 'adhoc' not in filename.lower():
                    last_data_loader_index = i

        for i, filename in enumerate(filenames):
            logging.debug(f'Processing {filename}')
            count_file += 1
            file_path = os.path.join(folder_path_sql, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    sql_content = file.read()

                logging.info(f'{count_file}: {filename}')
                sql_content = self.beautify_sql(sql_content)

                source_table_names, staging_table_names = self.extract_table_names(sql_content)

                is_last_step = (i == last_data_loader_index)
                dfa_file_name = self.print_table_names(filename.lower(), source_table_names, staging_table_names,
                                                       is_last_step)

                key = (self.app_name, self.feed_name, self.initials_6char, 'source_table_' + dfa_file_name)
                data_store.set_data(key, source_table_names)

                self.file_service.create_file(dfa_file_name, sql_content)
                logging.info('\n')
            except OSError as e:
                logging.error(f'Error reading {file_path}: {e}')

        key_dict = (self.app_name, self.feed_name, self.initials_6char, 'staging_table_dict')
        data_store.set_data(key_dict, self.staging_table_dict)

        self.update_source_table_names()
        # self.file_service.update_table_name(self.staging_table_dict)
        logging.debug(f'Updated Steps after Table name update is {self.steps}')

        return self.steps

    def extract_table_names(self, sql_content):
        pattern_source = re.compile(r'\b(?:FROM|JOIN|USING|MERGE)\s+`?([\w.-]+)`?', re.IGNORECASE)  # Source
        pattern_staging = re.compile(r'\b(?:UPDATE TABLE|TRUNCATE TABLE|INSERT INTO|REPLACE TABLE)\s+`?([\w.-]+)`?',
                                     re.IGNORECASE)  # Staging

        source_table_names = set(pattern_source.findall(sql_content))
        staging_table_names = set(pattern_staging.findall(sql_content))

        if len(staging_table_names) > 1:
            logging.error(f"ERROR: More than 1 Staging Table in {sql_content}")

        return source_table_names, staging_table_names

    def print_table_names(self, filename, source_table_names, staging_table_names, is_last_step):
        step = Step()
        suffix, updated_filename, base_path, sql_type, base_table_name = self.suffix_determiner.determine_suffix_and_base_path(
            filename, is_last_step)
        if suffix != '(s/m/l/h)':
            logging.info(
                f"\tDFA SQL File Name: {base_path}_{self.initials_6char}{suffix}{updated_filename}")
            step.add_gcs_bucket_name(f'{base_path}_{self.initials_6char}{suffix}{updated_filename}')

        dfa_table_name = f'{base_table_name}{suffix}{updated_filename.replace(".sql", "")}'
        logging.info(f"\tDFA Table Name: {dfa_table_name}")
        step.add_table_name(dfa_table_name)

        if len(staging_table_names) > 0 and 'adhoc' not in filename.lower():
            self.staging_table_dict[staging_table_names.pop().lower()] = dfa_table_name

        for table_name in source_table_names:
            table_name = table_name.lower()
            logging.info(f'\t\t{table_name}')
            step.add_de_table(table_name)

        # if is_last_step:
        #     step.is_master_table()

        self.steps.add_step(step)

        return f'{sql_type}_{self.initials_6char}{suffix}{updated_filename}'  # Dfa File Name

    def update_source_table_names(self):
        for step in self.steps.get_all_steps():
            table_names = step.get_all_de_tables().copy()  # Make a copy of the list
            for table_name in table_names:
                logging.debug(table_name)
                # Update DE Staging Table with DFA Table Name
                if table_name in self.staging_table_dict:
                    logging.debug(f"Updating {table_name} to {self.staging_table_dict[table_name]}")
                    step.update_de_table(table_name, self.staging_table_dict[table_name])
                # Remove Tables not starting with dfa or prj: Remove temporary table names
                elif table_name[:3] not in ['dfa', 'prj']:
                    logging.debug(f"Removing {table_name}")
                    step.delete_de_table(table_name)

    def beautify_sql(self, sql_query):
        return sqlparse.format(sql_query, reindent=True, keyword_case='upper')

    def add_ccpa_steps(self, initials_6char, steps: Steps):
        logging.info("Adding CCPA Steps")
        ccpa_step_added = False

        for step in steps.get_all_steps():
            gcs_bucket_name = step.gcs_bucket_name
            table_name = step.table_name

            if ('data_loader_'+initials_6char + 'm') in gcs_bucket_name:
                if not ccpa_step_added:
                    ccpa_step = Step()
                    ccpa_step.add_gcs_bucket_name(gcs_bucket_name + '_ccpa')
                    ccpa_step.add_table_name(table_name + '_ccpa')
                    ccpa_step.add_de_table(table_name)
                    ccpa_step.is_master_table = True
                    steps.add_step(ccpa_step)
                    ccpa_step_added = True

            if 'data_extract' in gcs_bucket_name:
                de_tables = step.get_all_de_tables()
                if de_tables:
                    de_tables[0] = de_tables[0] + '_ccpa'

        logging.info("Added CCPA Steps")
        return steps
