import os


def rename_json_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json') or filename.endswith('.JSON'):
            file_path = os.path.join(folder_path, filename)
            new_filename = initials_6char + filename.replace('_data_loader', '').replace('_tbl', '').lower()
            new_file_path = os.path.join(folder_path, new_filename)
            os.rename(file_path, new_file_path)
            print(f'Renamed "{filename}" to "{new_filename}"')
        else:
            print(f'ERROR: filename does not end with .JSON or .json: {filename}')


initials_6char = r'epvhwt' + 's'
rename_json_files(
    r'C:\Users\SRIZVI13\dfa-gcp-campaign-service-terraform\bq_schema\qa\campaign_service\op461_esp_new_vehicle_warranty')
