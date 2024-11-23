import re

def replace_create_with_truncate_and_insert(file_content):
    # Define a regex pattern to match 'CREATE OR REPLACE TABLE `table_name` AS'
    pattern = re.compile(r'CREATE\s+OR\s+REPLACE\s+TABLE\s+`?([\w.-]+)`?\s+AS', re.IGNORECASE)

    # Function to replace matched pattern
    def replacement(match):
        table_name = match.group(1)
        return f"TRUNCATE TABLE '{table_name}';\n\nINSERT INTO '{table_name}'"

    # Use the sub method to replace patterns
    result = pattern.sub(replacement, file_content)

    return result

# Example usage
file_content = """
--AUTHOR:          KAILAA SRI BR (KBR)
--DFA STANDARDS:   SRIZVI13
--Date:            11/01/2024
--UPSTREAM TABLE:  prj-dfdm-10-cdm-p-0010.bq_cdm_core_fdp_dmc_vw.scr_vehicle_denorm_vw
--                 dfa_campaign_service_op824_esp_fplp_marketing_fz_db.flpmkts04_op824_outbound_filtered


CREATE OR REPLACE TABLE `dfa_campaign_service_op824_esp_fplp_marketing_fz_db.flpmkts05_op824_splits_by_month` AS
SELECT outbound.consumer_id,
       outbound.country_code,
       outbound.vehicle_ownership_cycle_number,
       outbound.dealer_key,
       outbound.vehicle_assigned_dealer_key,
       outbound.consumer_cm_key,
       outbound.address_quality_ind,
       outbound.consumer_type_code,
       outbound.organization_name_line_1,
       outbound.individual_title,
       outbound.individual_first_name,
       outbound.individual_middle_initial,
       outbound.individual_last_name,
       outbound.individual_last_name_suffix,
       outbound.consumer_address_line_1,
       outbound.consumer_address_line_2,
       outbound.city_or_secondary_country_div,
       outbound.state_or_primary_cntry_div_cd,
       outbound.postal_cd_first_six_positions,
       outbound.postal_cd_last_four_positions,
       outbound.phone_number,
       outbound.preferred_language_code,
       outbound.vin_id,
       outbound.vehicle_model_year,
       outbound.vehicle_model,
       outbound.acquisition_date,
       outbound.local_sales_type_key,
       outbound.disposal_ind,
       outbound.new_or_used_ind,
       outbound.selling_dealer_key,
       outbound.predicted_odometer_miles,
       outbound.pred_odometer_update_date,
       outbound.warranty_start_date,
       outbound.household_demographics_key,
       outbound.vehicle_body_style_series,
       outbound.vehicle_body_style_series_code,
       outbound.vehicle_make,
       outbound.individual_age,
       outbound.individual_gender,
       outbound.df_months,
       outbound.df_email,
       outbound.vehicle_program_type_code,
       outbound.derived_acquisition_type,
       outbound.finance_account_end_date,
       outbound.finance_month_wise,
       outbound.member_id,
       outbound.hh_income_range_code,
       outbound.safe_email_flg,
       number_of_finance_payments,
       score_2009_value AS esp_ford_score,
       score_2010_value AS esp_lincoln_score,
       'MNTH' AS df_seg_mnth
FROM `dfa_campaign_service_op824_esp_fplp_marketing_fz_db.flpmkts04_op824_outbound_filtered` outbound
JOIN `prj-dfdm-10-cdm-p-0010.bq_cdm_core_fdp_dmc_vw.scr_vehicle_denorm_vw` den ON outbound.consumer_id = den.consumer_id
AND outbound.vin_id = den.vin
WHERE (((vehicle_make = 'LINCOLN')
        AND (df_months IN (7,
                           29,
                           35,
                           41,
                           44,
                           46)))
       OR ((vehicle_make IN ('FORD'))
           AND (df_months IN (7,
                              17,
                              23,
                              29,
                              32,
                              33,
                              34)))
       OR ((df_months IN (4,
                          5,
                          6))
           AND predicted_odometer_miles<=10000)
       OR (vehicle_make IN ('FORD')
           AND (derived_acquisition_type = 'RET')
           AND (df_months >= 3)
           AND (df_months <= 31)
           AND (predicted_odometer_miles >= 30000)
           AND (predicted_odometer_miles <= 34000))
       OR (df_months=8
           AND predicted_odometer_miles >=12000
           AND derived_acquisition_type ='RET'));
"""
updated_content = replace_create_with_truncate_and_insert(file_content)
print(updated_content)