import logging

from backend.config.logging_config import configure_logging

# Configure logging
configure_logging()


class SuffixDeterminer:
    def __init__(self, app_name, feed_name, initials_6char):
        self.app_name = app_name
        self.feed_name = feed_name
        self.initials_6char = initials_6char

    def determine_suffix_and_base_path(self, filename, is_last_step=False):
        app_name_formatted = self.app_name.lower().replace('gcp', 'dfa').replace('_', '-')
        feed_name_formatted = self.feed_name.replace("_", "-").lower()

        base_path = f"gs://{app_name_formatted}-{feed_name_formatted}-source-qa/sql-scripts/data_loader"
        sql_type = 'data_loader'
        base_table_name = f"{app_name_formatted.replace('-', '_')}_{feed_name_formatted.replace('-', '_')}_fz_db.{self.initials_6char}"

        if 'merge' in filename:
            suffix = 'h'
            base_path = f"gs://{app_name_formatted}-{feed_name_formatted}-source-qa/sql-scripts/data_merge"
            sql_type = 'data_merge'
            filename = filename.replace("_data_merge", "")
        elif 'purge' in filename:
            suffix = 'h'
            base_path = f"gs://{app_name_formatted}-{feed_name_formatted}-source-qa/sql-scripts/data_purge"
            sql_type = 'data_purge'
            filename = filename.replace("_data_purge", "")
        elif 'history' in filename:
            suffix = 'h'
            filename = filename.replace("_data_loader", "")
        elif 'reference' in filename:
            suffix = 'l'
        elif 'loader' in filename:
            suffix = 'm' if is_last_step else 's'
            filename = filename.replace("_data_loader", "")
        elif 'extract' in filename:
            suffix = 'm'
            base_path = f"gs://{app_name_formatted}-{feed_name_formatted}-source-qa/sql-scripts/data_extract"
            sql_type = 'data_extract'
            filename = filename.replace("_data_extract", "")
        else:
            suffix = '(s/m/l/h)'
            base_path = f"gs://{app_name_formatted}-{feed_name_formatted}-other"
            logging.error(f'\tDifferent Tables in {filename}:')

        return suffix, filename, base_path, sql_type, base_table_name
