import os


def rename_sql_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.sql') or filename.endswith('.SQL'):
            file_path = os.path.join(folder_path, filename)
            if '_data_loader' in filename:
                new_filename = 'data_loader_' + initials_6char + 's' + filename.replace('_data_loader', '').replace(
                    '_tbl', '').lower()
            elif '_data_extract' in filename:
                new_filename = 'data_extract_' + initials_6char + 'm' + filename.replace('_data_extract', '').replace(
                    '_tbl', '').lower()

            new_file_path = os.path.join(folder_path, new_filename)
            os.rename(file_path, new_file_path)
            print(f'Renamed "{filename}" to "{new_filename}"')
        else:
            print(f'ERROR: filename does not end with ..sql: {filename}')


initials_6char = r'epfplp'
rename_sql_files(r'C:\Users\SRIZVI13\50884_dfa_campaign_service_op918_esp_fplp\scripts\sql')
