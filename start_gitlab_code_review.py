import base64
import os

from code_review_system.add_line_number import prefix_line_numbers
from code_review_system.code_review_output import set_note_template, blank_file_note_format
from code_review_system.llm.llm_manager import LLMManager
from code_review_system.llm.code_review.output_parser import CodeReviewResult
from langchain_core.exceptions import OutputParserException
from code_review_system.gitlab.create_gitlab_mr_note import create_gitlab_mr_note
from code_review_system.vcs.vcs_manager import VCSManager
from code_review_system.file_filter import is_code_file

def start_gitlab_code_review(repo_params, code_review_chain):
    """
    Function to initiate GitLab code review.

    :param repo_params: Dictionary containing repository and merge request parameters.
    :param code_review_chain: Code review chain for LLM.
    :return: True if the review process completes; otherwise, False.
    """
    print("Starting GitLab code review process...")
    
    changes = repo_params.get('changes')
    
    batch = repo_params.get('batch')
    project_object = repo_params.get('project_object')
    commit = repo_params.get('commit_message')

    provider = repo_params.get('provider')
    
    if provider == "gitlab":
        print("Provider is GitLab. Fetching project and merge request objects...")
        try:
            project_object = VCSManager().get_project_object(
                url_instance=repo_params.get('url_instance'),
                project_id=project_object.id,
                access_token=os.getenv('GITLAB_KEY'),
                token_type="private_token"
            )
            print(f"Fetched project object with ID: {project_object.id}")
        except Exception as e:
            print("Error fetching project object:", e)
            return False
        
        try:
            merge_request_object = VCSManager().get_merge_request_object(
                project_object=project_object,
                merge_request_id=repo_params.get('merge_request_object').iid
            )
            print("Fetched merge request object.")
        except Exception as e:
            print("Error fetching merge request object:", e)
            return False
    else:
        print("Provider is not GitLab. Using provided merge request object...")
        merge_request_object = repo_params.get('merge_request_object')
    
    is_vulnerability_test_enabled = repo_params.get('is_vulnerability_test_enabled')
    print(f"Vulnerability test enabled: {is_vulnerability_test_enabled}")
    
    source_branch = changes.get('source_branch')
    diff_refs = changes.get('diff_refs', {})
    source_sha = diff_refs.get('start_sha')
    base_sha = diff_refs.get('base_sha')
    head_sha = diff_refs.get('head_sha')

    ignored_files = repo_params.get('ignored_files')
    
    code_review_comment = ""
    
    if not ignored_files:
        repo_params['ignore_files'] = []
        print("No ignore_files provided; defaulting to an empty list.")
    
    for key, value in batch.items():
        path = key
        print(f"Processing file: {path}")
        
        if not is_code_file(path):
            print(f"Skipping non-code file: {path}")
            continue

        if not value and path not in ignored_files:
            try:
                file_obj = project_object.files.get(file_path=path, ref=source_branch)
                code = file_obj.content
                decoded_code = base64.b64decode(code).decode('utf-8')
            except Exception as e:
                print(f"Error fetching or decoding content for file {path}:", e)
                continue

            if decoded_code.strip() == "":
                code_review_comment += blank_file_note_format(path)
            else:
                lined_code = prefix_line_numbers(decoded_code)
                try:
                    llm_response = LLMManager().llm_invoke_with_retry(
                        code_review_chain,
                        {"code": lined_code}
                    )
                    
                    if isinstance(llm_response, CodeReviewResult):
                        response_dict = llm_response.dict()
                        comments_data = response_dict.get('comments', {})
                    else:
                        comments_data = llm_response

                    if comments_data is None:
                        print(f"No comments data returned for file: {path}")
                        continue

                    result = list(map(lambda item: set_note_template(item[0], item[1], path, provider), comments_data.items()))
                    
                    if not result:
                        print(f"No comments found for file: {path}")
                        continue
                        
                    notes, line_numbers = zip(*result)
                    mr_note_params = {
                        'project_id': project_object.id,
                        'merge_request_object': merge_request_object,
                        'line_numbers': line_numbers,
                        'notes': notes,
                        'path': path,
                        'source_sha': source_sha,
                        'base_sha': base_sha,
                        'head_sha': head_sha
                    }
                    print(f"Creating GitLab merge request note for file: {path}")
                    create_gitlab_mr_note(mr_note_params)
                except OutputParserException as e:
                    print("OutputParserException during LLM invocation:")
                    print("Error in LLM:", e)
                    continue
                except Exception as e:
                    print(f"Unexpected error processing {path}: {str(e)}")
                    continue
        else:
            print(f"File {path} has been ignored.")
    
    print("GitLab code review process completed successfully.")
    return True
