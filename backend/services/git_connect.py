import logging
import os
import re

from git import Repo, GitCommandError, InvalidGitRepositoryError
from numpy.f2py.auxfuncs import throw_error

from backend.config.logging_config import configure_logging

# Configure logging
configure_logging()

class GitConnect:
    def parse_github_url(self, url):
        try:
            match = re.match(r"https://github.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)", url)
            if match:
                username, repository, branch, folder = match.groups()
                ssh_url = f"git@github.com:{username}/{repository}.git"
                return ssh_url, branch, folder
            else:
                logging.error("Invalid GitHub URL format.")
                return None
        except Exception as e:
            logging.error(f"Error parsing GitHub URL: {e}")
            return None

    def read_files_from_github(self, repo_url, branch_name, folder_path, local_repo_path):
        full_local_repo_path = os.path.join(local_repo_path, repo_url.split("/")[-1].replace('.git', ''))

        logging.info(f"Preparing to clone repository from {repo_url} to {full_local_repo_path}")

        try:
            if not os.path.exists(full_local_repo_path):
                logging.info(f"Cloning repository from {repo_url} to {full_local_repo_path}")
                repo = Repo.clone_from(repo_url, full_local_repo_path)
            else:
                logging.info(f"Repository found locally at: {full_local_repo_path}")
                repo = Repo(full_local_repo_path)
                origin = repo.remotes.origin
                origin.fetch()

            repo.git.checkout(branch_name)
            logging.info(f"Checked out branch: {branch_name}")

            # Pull the latest changes to ensure the repository is up-to-date
            repo.git.pull('origin', branch_name)
            logging.info(f"Pulled latest changes for branch: {branch_name}")

            target_folder = os.path.join(full_local_repo_path, folder_path)
            if not os.path.exists(target_folder):
                logging.warning(f"Target folder {target_folder} does not exist in the repository.")
                return None

            return target_folder

        except GitCommandError as e:
            logging.error(f"Git command error: {e}")
            raise "Cloning Repository have issues. Try locally at your end. For Help, reach out to Syed Mohd Haider Rizvi"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise "Cloning Repository have issues. For Help, reach out to Syed Mohd Haider Rizvi"

        return None

    def get_local_absolute_path(self, github_url, clone_or_data_path):
        try:
            result = self.parse_github_url(github_url)
            if result:
                github_repo_url, branch, folder = result
                logging.info(f"SSH Git URL: {github_repo_url}")
                logging.info(f"Branch: {branch}")
                logging.info(f"Folder: {folder}")
            else:
                logging.info("Invalid GitHub URL format.")

            local_absolute_path = self.read_files_from_github(github_repo_url, branch, folder, clone_or_data_path)
            logging.info(f'Data Loaded Successfully at Path: {local_absolute_path}')
            return local_absolute_path
        except Exception as e:
            logging.error(f"Error getting local absolute path: {e}")
            raise e

    def push_folder_to_github(self, repo_url, folder_path, branch_name, commit_message, local_repo_path=''):
        full_local_repo_path = folder_path

        try:
            if not os.path.exists(full_local_repo_path):
                os.makedirs(full_local_repo_path)
                logging.info(f"Created directory: {full_local_repo_path}")

            # Check if the directory is a valid Git repository
            try:
                repo = Repo(full_local_repo_path)
            except InvalidGitRepositoryError:
                repo = Repo.init(full_local_repo_path)
                logging.info(f"Initialized new Git repository at: {full_local_repo_path}")

            # Add remote if not already present
            if 'origin' not in [remote.name for remote in repo.remotes]:
                repo.create_remote('origin', repo_url)
                logging.info(f"Added remote 'origin' with URL: {repo_url}")

            # Fetch the latest changes from the remote repository
            origin = repo.remotes.origin
            origin.fetch()

            # Force checkout the master branch
            repo.git.checkout('master', force=True)

            # Pull the latest changes from the master branch
            repo.git.pull('origin', 'master')

            # Check if the branch exists locally
            if branch_name in repo.heads:
                repo.git.checkout(branch_name)
            else:
                # Create a new branch from the master branch
                repo.git.checkout('HEAD', b=branch_name)

            # Add all files from the local_repo_path to the repository
            repo.git.add('--all')

            # Commit the changes
            repo.index.commit(commit_message)

            # Merge master into the branch with the 'theirs' strategy to resolve conflicts
            repo.git.merge('master', strategy_option='theirs')

            # Push the new branch to the remote repository
            origin.push(refspec=f"{branch_name}:{branch_name}")

            logging.info(f"Successfully pushed {local_repo_path} to {repo_url} on branch {branch_name}")
        except GitCommandError as e:
            logging.error(f"Git command error: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}", exc_info=True)