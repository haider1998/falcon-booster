import os


def add_header_to_sql_files(folder_path):
    header = """/*--AUTHOR:         Vasantha Priya(pvasant6)
--DFA STANDARDS:    srizvi13
--Date:             10/03/2024
--UPSTREAM TABLE:   dfa_campaign_service_op6212_espflfplp_marketing_fz_db.espmrks07_op6212_exinvmail
                    prj-dfdm-10-cdm-p-0010.bq_cdm_core_fdp_dmc_vw.uvw_vomart_curr_vw
 */
 
"""
    for filename in os.listdir(folder_path):
        if filename.endswith('.sql') or filename.endswith('.SQL'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r+', encoding='utf-8') as file:
                content = file.read()
                file.seek(0, 0)
                file.write(header + '\n' + content)
            print(f'Added header to "{filename}"')
        else:
            print(f'ERROR: filename does not end with .sql: {filename}')


add_header_to_sql_files(r'C:\Users\SRIZVI13\50884_dfa_campaign_service_op918_esp_fplp\scripts\sql')
