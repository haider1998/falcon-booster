import os


def print_files(folder_path):
    filenames = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.json') or filename.endswith('.JSON'):
            filenames.append(f'"{filename.replace(".json", "").replace(".JSON", "")}"')
        else:
            print(f'ERROR: filename not ends with .JSON or .json: {filename}')

    print(','.join(filenames))


print_files(r'C:\Users\SRIZVI13\dfa-gcp-campaign-service-terraform\bq_schema\qa\campaign_service\op824_esp_fplp_marketing')
