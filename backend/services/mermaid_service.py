# file: backend/services/mermaid_service.py
import logging
from typing import List

from backend.config.logging_config import configure_logging
from backend.models.Step import Step
from backend.services.interfaces import MermaidServiceInterface

# Configure logging
configure_logging()


def get_extra_steps(dropzone_sftp, gcs_bucket):
    # Add extra steps
    extra_steps = ["PROFILE", "ALERT", "DATA EXTRACT", "HEADER AND TRAILER", "COPY_TO_GCSBUCK", "SFTP", "HISTORY", "ARCHIVE",
                   "SUCCESS EMAIL"]

    if not gcs_bucket:
        extra_steps.remove("COPY_TO_GCSBUCK")
        logging.info("Remove GCS Bucket in Design")

    if not dropzone_sftp:
        extra_steps.remove("SFTP")
        logging.info("Remove SFTP in Design")

    return extra_steps


class MermaidService(MermaidServiceInterface):
    def generate_mermaid_code(self, dropzone_sftp: bool, dropzone_gcs_bucket: bool, steps: List[Step],
                              output_filename: str) -> str:
        """Converts Steps object to a Mermaid graph definition with Start and End nodes and custom styles."""

        mermaid_code = "graph TD;\n"

        # Define custom styles
        mermaid_code += """
            classDef stepStyle fill:#2962FF,stroke:#2962FF,stroke-width:2px,color:#FFFFFF;
            classDef startEndStyle fill:#00C853,stroke:#00C853,stroke-width:2px,color:#FFFFFF;
            classDef decisionStyle fill:#FFAB00,stroke:#FFAB00,stroke-width:2px,color:#FFFFFF;
            """

        # Start Node with custom style
        mermaid_code += "StartWF[\"Start WF\"] --> Step1;\n"
        mermaid_code += "class StartWF startEndStyle;\n"

        # data extract step
        data_extract_step: Step = None

        # data history step
        data_history_step: Step = None

        step_count = 1

        step_sequence = 1

        # Process original steps
        for i, step in enumerate(steps.get_all_steps()):

            if 'adhoc' in step.gcs_bucket_name:
                continue

            # Data Extract Step
            if 'data_extract' in step.gcs_bucket_name:
                logging.info(f'Data Extract Step \n{step}')
                data_extract_step = step
                step_count = 0
                continue

            # Data History Step
            if 'history' in step.gcs_bucket_name:
                logging.info(f'Data History Step \n{step}')
                data_history_step = step
                step_count = 0
                continue

            step_id = f"Step{step_sequence}"
            gcs_bucket = step.gcs_bucket_name or ""
            table_name = step.table_name or ""
            source_tables = "<br>".join(step.get_all_de_tables()) or ""

            if 'ccpa' in gcs_bucket:
                node_label = (
                    f"""<b>Step {step_sequence}</b><br>"""
                    f"""<b>CCPA</b><br>"""
                    f"""<b>Table:</b> {table_name}<br>"""
                    f"""<b>Source Tables:</b><br>{source_tables}"""
                )
            else:
                node_label = (
                    f"""<b>Step {step_sequence}</b><br>"""
                    f"""<b>DATA LOADER</b><br>"""
                    f"""<b>GCS:</b> {gcs_bucket}<br>"""
                    f"""<b>Table:</b> {table_name}<br>"""
                    f"""<b>Source Tables:</b><br>{source_tables}"""
                )

            mermaid_code += f'{step_id}["{node_label}"];\n'
            mermaid_code += f"class {step_id} stepStyle;\n"

            # Add decision node
            decision_id = f"Decision{step_sequence}"
            mermaid_code += f'{decision_id}{{"Is Success?"}}:::decisionStyle;\n'

            # Connect step to decision
            mermaid_code += f"{step_id} --> {decision_id};\n"

            # Connect decision to next step if successful
            if i < len(steps.get_all_steps()):
                next_step_id = f"Step{step_sequence + 1}"
                mermaid_code += f"{decision_id} -- Yes --> {next_step_id};\n"

            # Connect decision to a single abandoned node and then to EndWF
            mermaid_code += f"{decision_id} -- No --> Abandoned[\"ABANDONED\"];\n"
            mermaid_code += f"class Abandoned stepStyle;\n"

            step_sequence += 1

        # Connect the single abandoned node to EndWF
        mermaid_code += "Abandoned --> EndWF;\n"

        # Add extra steps
        extra_steps = get_extra_steps(dropzone_sftp, dropzone_gcs_bucket)

        last_step_id = f"Step{len(steps.get_all_steps())}"
        step_number = step_sequence + step_count
        for i, extra_step in enumerate(extra_steps):
            extra_step_id = f"Step{step_number}"
            decision_id = f"Decision{step_number}"

            if 'DATA EXTRACT' == extra_step:
                gcs_bucket = data_extract_step.gcs_bucket_name or ""
                # table_name = data_extract_step.table_name or ""
                source_tables = "<br>".join(data_extract_step.get_all_de_tables()) or ""
                node_label = (
                    f"""<b>Step {step_number}</b><br>"""
                    f"""<b>{extra_step}</b><br>"""
                    f"""<b>GCS:</b> {gcs_bucket}<br>"""
                    f"""<b>Source Tables:</b><br>{source_tables}"""
                )
            elif 'HISTORY' == extra_step:
                if data_history_step is not None:
                    logging.info(f'Data History Step \n{data_history_step}')
                    gcs_bucket = data_history_step.gcs_bucket_name or ""
                    table_name = data_history_step.table_name or ""
                    source_tables = "<br>".join(data_history_step.get_all_de_tables()) or ""
                    node_label = (
                        f"""<b>Step {step_number}</b><br>"""
                        f"""<b>{extra_step}</b><br>"""
                        f"""<b>GCS:</b> {gcs_bucket}<br>"""
                        f"""<b>Table:</b> {table_name}<br>"""
                        f"""<b>Source Tables:</b><br>{source_tables}"""
                    )
                else:
                    logging.info('Data History Step not found. Skip History Step')
                    continue
            else:
                node_label = f"""<b>Step {step_number}:\n{extra_step}</b>"""

            mermaid_code += f'{extra_step_id}["{node_label}"];\n'
            mermaid_code += f"class {extra_step_id} stepStyle;\n"

            # Add decision node
            mermaid_code += f'{decision_id}{{"Is Success?"}}:::decisionStyle;\n'

            # # Connect previous step to current extra step
            # if i == 0:
            #     mermaid_code += f"{last_step_id} --> {extra_step_id};\n"

            # Connect extra step to decision
            mermaid_code += f"{extra_step_id} --> {decision_id};\n"

            # Connect decision to next extra step if successful
            if i < len(extra_steps) - 1:
                next_step_id = f"Step{step_number + 1}"
                mermaid_code += f"{decision_id} -- Yes --> {next_step_id};\n"
            else:
                # Connect the last extra step's decision to EndWF
                mermaid_code += f"{decision_id} -- Yes --> EndWF;\n"

            # Connect decision to a single abandoned node and then to EndWF
            mermaid_code += f"{decision_id} -- No --> Abandoned[\"ABANDONED\"];\n"

            last_step_id = decision_id

            step_number += 1

        # End Node with custom style
        mermaid_code += "EndWF[\"End WF\"];\n"
        mermaid_code += "class EndWF startEndStyle;\n"

        with open(output_filename, 'w', encoding='utf-8') as mmdfile:
            mmdfile.write(mermaid_code)

        return mermaid_code
