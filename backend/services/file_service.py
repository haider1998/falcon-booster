# backend/services/file_service.py
import datetime
import logging
import os
import re

from backend.config.logging_config import configure_logging
from backend.config.logging_config_filter import CorrelationIdFilter
from backend.repositories.data_store import DataStore
from backend.services.git_connect import GitConnect

# Configure logging
correlation_filter = configure_logging()

data_store = DataStore()
git_service = GitConnect()


class FileService:
    def __init__(self, folder_path, app_name, feed_name, initials_6char, dfa_repo_name, data_engineer_name,
                 data_engineer_cds_id, software_engineer_cds_id, storage_type, ccpa):
        self.folder_path = folder_path
        self.app_name = app_name
        self.feed_name = feed_name
        self.initials_6char = initials_6char
        self.dfa_repo_name = dfa_repo_name
        self.data_engineer_name = data_engineer_name
        self.data_engineer_cds_id = data_engineer_cds_id
        self.software_engineer_cds_id = software_engineer_cds_id
        self.storage_type = storage_type
        self.ccpa = ccpa
        self._ensure_folder_exists()

    def _ensure_folder_exists(self):
        os.makedirs(self.folder_path, exist_ok=True)

    def create_file(self, file_name, file_content):
        file_path = os.path.join(self.folder_path, file_name)
        with open(file_path, 'w') as file:
            file.write(file_content)
        logging.debug(f'File "{file_name}" created at "{self.folder_path}"')

    def create_terraform_file(self):
        main_folder_path = os.path.dirname(os.path.dirname(self.folder_path))
        terraform_content = f"""APPLICATION={self.app_name.upper().replace('GCP_', '')}
FEED={self.feed_name.lower()}"""
        file_path = os.path.join(main_folder_path, 'tektonconfig.txt')
        with open(file_path, 'w') as file:
            file.write(terraform_content)
        logging.debug(f'File tektonconfig.txt created at "{main_folder_path}"')

    def create_setup_file(self):
        main_folder_path = os.path.dirname(os.path.dirname(self.folder_path))
        main_folder_path = main_folder_path + '/setup'
        os.makedirs(main_folder_path, exist_ok=True)
        instructions_content = f"""#Include the archival bucket name and any additional instructions for the Release Manager if needed
dfa-{self.storage_type.lower()}-archive-""" + r'{ENV}'
        file_path = os.path.join(main_folder_path, 'instructions.txt')
        with open(file_path, 'w') as file:
            file.write(instructions_content)
        logging.debug(f'File instructions.txt created at "{main_folder_path}"')

    def update_table_name(self, staging_table_dict):
        logging.info("test1")
        for file_name in os.listdir(self.folder_path):
            logging.info("test2")
            if file_name.endswith('.sql'):
                file_path = os.path.join(self.folder_path, file_name)
                with open(file_path, 'r') as file:
                    file_content = file.read()
                logging.info("test3")
                file_content = self.add_header_to_sql_files(file_name, ) + '\n' + file_content
                logging.info("test4")
                for key, value in staging_table_dict.items():
                    logging.debug(f'Finding "{key}" in file "{file_name}"')
                    if re.search(re.escape(key), file_content, re.IGNORECASE):
                        replacement = value + '_ccpa' if self.ccpa and 'data_extract' in file_name else value
                        file_content = re.sub(re.escape(key), replacement, file_content, flags=re.IGNORECASE)
                        logging.debug(f'Replaced "{key}" with "{replacement}" in file "{file_name}"')
                logging.info("test5")
                file_content = self.replace_create_with_truncate_and_insert(file_content)
                logging.info("test6")
                with open(file_path, 'w') as file:
                    file.write(file_content)
                logging.info("test7")
                logging.debug(f'File "{file_name}" updated at "{self.folder_path}"')

    def add_header_to_sql_files(self, file_name):
        # No need to add header in Extract Files
        if 'extract' in file_name:
            return ''

        key = (self.app_name, self.feed_name, self.initials_6char, 'source_table_' + file_name)
        tables = data_store.get_data(key)
        filtered_tables = [table for table in tables if table[:3] in ['dfa', 'prj', 'for']]

        source_tables = "\n--                 ".join(filtered_tables) or ""
        sysdate = datetime.datetime.now().strftime("%m/%d/%Y")

        header = f"""--AUTHOR:          {self.data_engineer_name.upper()} ({self.data_engineer_cds_id.upper()})
--DFA STANDARDS:   {self.software_engineer_cds_id.upper()}
--Date:            {sysdate}
--UPSTREAM TABLE:  {source_tables}
        
        """

        return header

    def replace_create_with_truncate_and_insert(self, file_content):
        # Define a regex pattern to match 'CREATE OR REPLACE TABLE `table_name` AS'
        pattern = re.compile(r'CREATE\s+OR\s+REPLACE\s+TABLE\s+`?([\w.-]+)`?\s+AS', re.IGNORECASE)

        # Function to replace matched pattern
        def replacement(match):
            table_name = match.group(1)
            return f"TRUNCATE TABLE `{table_name}`;\n\n\nINSERT INTO `{table_name}`"

        # Use the sub method to replace patterns
        result = pattern.sub(replacement, file_content)

        return result

    def create_feed_repository(self):
        logging.info(f'Creating Feed Repository for {self.app_name} - {self.feed_name}')
        staging_table_dict = data_store.get_data(
            (self.app_name, self.feed_name, self.initials_6char, 'staging_table_dict'))
        logging.info(f'Got Staging Table Dict {staging_table_dict}')
        self.update_table_name(staging_table_dict)
        logging.info(f'Updated Tables in all files')
        self.create_terraform_file()
        logging.info(f'Created Terraform file')
        self.create_setup_file()
        logging.info(f'Created Setup file')

        git_repo_link = f'git@github.com:<Project Name>/{self.dfa_repo_name}.git' #TODO: Update Project Name

        path = f'tmp/resource/{self.dfa_repo_name}'

        git_service.push_folder_to_github(git_repo_link, path, f'feature/falcon-boost-setup/{self.software_engineer_cds_id.upper()}',
                                          f'Falcon Boost: Initial Commit: {self.software_engineer_cds_id.upper()}')

#
# file_service = FileService(r'C:\Users\SRIZVI13\IdeaProjects\DESQL\backend\resources\50884_dfa_campaign_service_op824_esp_fp_lp_marketing\scripts\sql', 'dfa_campaign_service', 'op824_esp_fp_lp_marketing', 'flpmkt', '', 'Kailaa', 'Kbr', 'srizvi13')
# file_service.create_feed_repository()
