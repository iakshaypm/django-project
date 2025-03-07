import base64
import os

from fastapi.responses import JSONResponse
from github import Github
from gitlab import GitlabAuthenticationError
from langchain_core.exceptions import OutputParserException

from authentication.utils.login import Login
from authentication.utils.oauth.token import Token, GitHubAppToken
from code_review_system.llm.code_review.output_parser import CodeReviewResult
from code_review_system.llm.llm_manager import LLMManager
from code_review_system.utils.add_line_number import prefix_line_numbers
from code_review_system.utils.code_review_output import set_note_template, blank_file_note_format
from code_review_system.utils.git_manager import VCSManager
from code_review_system.utils.log_manager import logger
from code_review_system.vulnerability_checker.tool_runner import quality_analysis_report
from constants import constants
from constants import messages
from database import models


async def create_github_mr_note(mr_note_params):
    """
    Creates Merge Request Comment on github
    :param mr_note_params:
    :return:
    """
    merge_request_object = mr_note_params.get('merge_request_object')
    line_nos = mr_note_params.get('line_numbers')
    notes = mr_note_params.get('notes')
    file_path = mr_note_params.get('path')
    # Function to create Merge Request Note
    for line_no, note in zip(line_nos, notes):
        try:
            merge_request_object.create_review(
                body=" ",
                event="COMMENT",
                comments=[
                    {
                        "path": file_path,  # File path relative to the repository
                        "position": int(line_no),  # Position in the diff (not absolute line number)
                        "body": note,  # Inline comment body
                    }
                ],
            )
        except Exception as e:
            logger.error(f"{messages.comment_error}, {e}")

async def create_gitlab_mr_note(mr_note_params):
    """
    Creates merge request note on gitlab
    :param mr_note_params:
    :return:
    """
    line_nos = mr_note_params.get('line_numbers')
    notes = mr_note_params.get('notes')
    merge_request_object = mr_note_params.get('merge_request_object')
    file_path = mr_note_params.get('path')
    start_sha = mr_note_params.get('source_sha')
    base_sha = mr_note_params.get('base_sha')
    head_sha = mr_note_params.get('head_sha')
    # Function to create Merge Request Note
    for line_no, note in zip(line_nos, notes):
        line_code = f"{start_sha}:{line_no}"
        try:
            merge_request_object.discussions.create({'body': note,
                                                     'position': {
                                                         'new_path': file_path,
                                                         'new_line': line_no,
                                                         'position_type': 'text',
                                                         'base_sha': base_sha,
                                                         'start_sha': start_sha,
                                                         'head_sha': head_sha
                                                     },
                                                'line_code': line_code
                                                     })
        except Exception as e:
            logger.error(f"{messages.comment_error} {e}, {file_path} : {line_no}")


async def start_github_code_review(repo_params, llm_manager_object, code_review_chain, quality_analysis_chain):
    """
    Function to initiate GitHub code review
    :param repo_params: Dictionary containing repository parameters
    :param llm_manager_object: LLM manager instance
    :param code_review_chain: Chain for code review
    :param quality_analysis_chain: Chain for quality analysis
    :return: None
    """
    git_manager_object = VCSManager()
    changes = repo_params.get('changes')
    project_object = repo_params.get('project_object')
    commit = repo_params.get('commit_message')
    merge_request_object = repo_params.get('merge_request_object')
    head_sha = merge_request_object.head.sha
    is_vulnerability_enabled = repo_params.get('is_vulnerability_test_enabled')
    source_branch = merge_request_object.head.ref
    code_review_comment = "### Vulnerability Report\n\n"

    project_instance = await models.Repository.get(project_id=project_object.id)
    ignored_files_dict = project_instance.ignored_files or {}
    ignore_file_flattened_list = [
        file_path
        for branch_files in ignored_files_dict.values()
        for file_path in branch_files
    ]
    ignored_paths = set(ignore_file_flattened_list)

    for change in changes:
        path = change.filename
        if change.status != constants.GITHUB_FILE_DELETED and path not in ignored_paths:
            try:
                code = project_object.get_contents(change.filename, ref=source_branch)
                decoded_code = code.decoded_content.decode('utf-8')

                if decoded_code.strip() == "":
                    code_review_comment += blank_file_note_format(path)
                    continue

                lined_code = prefix_line_numbers(decoded_code)

                llm_response = await LLMManager().llm_invoke_with_retry(
                    code_review_chain,
                    constants.CODE_REVIEW,
                    {
                        "code": lined_code,
                        "branch": source_branch,
                        "commit": commit,
                    })
                logger.info(messages.code_pass_to_llm_message)

                # Handle both Pydantic v1 and v2 methods
                if isinstance(llm_response, CodeReviewResult):
                    try:
                        # Try Pydantic v2 method first
                        response_dict = llm_response.dict()
                    except AttributeError:
                        try:
                            # Fall back to Pydantic v1 method
                            response_dict = llm_response.dict()
                        except AttributeError:
                            # If neither method exists, assume it's already a dict
                            response_dict = llm_response
                else:
                    response_dict = llm_response

                comments_data = response_dict.get('comments', [])

                # Process comments based on whether it's a list or dict
                if isinstance(comments_data, dict):
                    result = [set_note_template(str(line_no), comment, path)
                              for line_no, comment in comments_data.items()]
                elif isinstance(comments_data, list):
                    result = [set_note_template(str(item['line']), item['review'], path)
                              for item in comments_data]
                else:
                    logger.error(f"Unexpected comments_data type: {type(comments_data)}")
                    continue

                if result:  # Check if we have any results
                    notes, line_numbers = zip(*result)
                    mr_note_params = {
                        'merge_request_object': merge_request_object,
                        'line_numbers': line_numbers,
                        'notes': notes,
                        'path': path,
                        'head_sha': head_sha
                    }

                    if is_vulnerability_enabled:
                        try:
                            code_review_comment += f"\n### Vulnerability Scanned Report for {path}\n\n"
                            code_review_comment += await quality_analysis_report(
                                decoded_code,
                                path,
                                repo_params.get('model_preference'),
                                quality_analysis_chain
                            )
                            logger.info(f"{messages.added_vulnerability_note}")
                        except Exception as e:
                            logger.error(f"{messages.error_on_added_vulnerability_note}: {e}")

                    await create_github_mr_note(mr_note_params)

            except OutputParserException as e:
                logger.error(f'{messages.output_parser_exception}, path: {path}')
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing {path}: {str(e)}")
                continue
        else:
            logger.info(f'file have been ignored {path}')

    if is_vulnerability_enabled:
        await git_manager_object.mr_note_vulnerability(
            constants.GITHUB,
            merge_request_object,
            code_review_comment
        )

async def start_gitlab_code_review(repo_params, llm_manager_object, code_review_chain, quality_analysis_chain):
    """
    Function to initiate gitlab code review
    :param repo_params:
    :param llm_manager_object:
    :param code_review_chain:
    :param quality_analysis_chain:
    :return:
    """
    git_manager_object = VCSManager()
    changes = repo_params.get('changes')
    project_object = repo_params.get('project_object')
    commit = repo_params.get('commit_message')
    if repo_params.get('provider') == constants.GITLAB:
        project_object = await VCSManager().get_project_object(url_instance=repo_params.get('url_instance'),
                                                               project_id=project_object.id,
                                                               access_token=os.getenv('GITLAB_KEY'),
                                                               token_type=constants.private_token)
        merge_request_object = await (VCSManager().get_merge_request_object
                                       (project_object=project_object,
                                        merge_request_id=repo_params.get('merge_request_object').iid))
    else:
        merge_request_object = repo_params.get('merge_request_object')
    is_vulnerability_test_enabled = repo_params.get('is_vulnerability_test_enabled')
    source_branch = changes.get('source_branch')
    source_sha = changes.get('diff_refs').get('start_sha')
    base_sha = changes.get('diff_refs').get('base_sha')
    head_sha = changes.get('diff_refs').get('head_sha')
    logger.info(messages.received_source_branch_message)
    code_review_comment = "### Vulnerability Report\n\n"
    responses, codes, paths = [], [], []
    project_instance = await models.Repository.get(project_id=project_object.id)
    ignored_files_dict = project_instance.ignored_files or {}  # Handle cases where it's None
    ignore_file_flattened_list = [
        file_path
        for branch_files in ignored_files_dict.values()
        for file_path in branch_files
    ]
    ignored_paths = set(ignore_file_flattened_list)
    for change in changes['changes']:
        path = change.get('new_path')
        # Check if the file is not deleted and is not in the ignore list
        if not change.get('deleted_file') and path not in ignored_paths:
            code = project_object.files.get(file_path=change.get('new_path'), ref=source_branch).content
            decoded_code = base64.b64decode(code).decode('utf-8')
            if decoded_code.strip() == "":
                code_review_comment += blank_file_note_format(path)
            else:
                # Get the code with line number
                lined_code = prefix_line_numbers(decoded_code)
                paths.append(path)
                codes.append(lined_code)
                try:
                    llm_response = await LLMManager().llm_invoke_with_retry(
                        code_review_chain,
                        constants.CODE_REVIEW,
                        {
                            "code": lined_code,
                            "branch": source_branch,
                            "commit": commit,
                        })
                    logger.info(messages.code_pass_to_llm_message)
                    #Check the response is of dictionary
                    if isinstance(llm_response, CodeReviewResult):
                        # Convert Pydantic model to dictionary
                        response_dict = llm_response.dict()
                        comments_data = response_dict.get('comments', {})
                    else:
                        comments_data = llm_response.get('comments', {})

                    result = map(lambda item: set_note_template(item[0], item[1], path),
                                 comments_data.items())
                    notes, line_numbers = zip(*result)
                    mr_note_params = {'project_id': project_object.id,
                                      'merge_request_object': merge_request_object,
                                    'line_numbers' : line_numbers,
                                    'notes' : notes,
                                    'path' : path,
                                    'source_sha' : source_sha,
                                    'base_sha' : base_sha,
                                    'head_sha' : head_sha}
                    # Check the vulnerability is On/ Off
                    if is_vulnerability_test_enabled:
                        try:
                            code_review_comment += "\n\n#### Vulnerability Scanned Report for " + path + "\n\n"
                            code_review_comment += await quality_analysis_report(decoded_code, path,
                                                                           repo_params.get('model_preference'),
                                                                           quality_analysis_chain)
                            logger.info(f"{messages.added_vulnerability_note}")
                        except Exception as e:
                            logger.error(f"{messages.error_on_added_vulnerability_note}: {e}")
                    await create_gitlab_mr_note(mr_note_params)
                except OutputParserException as e:
                    logger.error(f'{messages.output_parser_exception}, path: {path}')
                    continue
        else:
            logger.info(f'file have been ignored {path}')
    if is_vulnerability_test_enabled:
        await git_manager_object.mr_note_vulnerability(constants.GITLAB, merge_request_object,
                                                        code_review_comment)


async def get_gitlab_code_changes(request):
    """
    Function to get the gitlab changes
    :param request:
    :return:
    """
    git_object = VCSManager()
    request_json = await request.json()
    # Get action of the merge request
    action = request_json.get('object_attributes').get('action')
    logger.info(f'{messages.webhook_action_message}{action}')
    if action in {constants.OPEN_ACTION, constants.REOPENED_ACTION, constants.UPDATE_ACTION}:
        project_id = request_json.get('project').get('id')
        # Get the user uuid from the merge request json
        user_uuid = request.headers.get('x-gitlab-token')
        repository_object = await models.Repository.filter(project_id=project_id).first()
        model_preference = None
        access_token = None
        ignored_files_dict = repository_object.ignored_files or {}  # Handle cases where it's None
        ignore_file_flattened_list = [
            file_path
            for branch_files in ignored_files_dict.values()
            for file_path in branch_files
        ]
        ignored_paths = set(ignore_file_flattened_list)

        if not repository_object:
            logger.error(f"Repository not found for project ID: {project_id}")
            return JSONResponse(status_code=404, content={"message": "Repository not found"})

        if not repository_object.is_integrated:
            return False

        try:
            if user_uuid:
                # Get the access_token for the gitlab repository
                access_token = await Token().check_expired(user_uuid)
                # Get the model preference of the corresponding user
                model_preference = await Login().check_for_model_preference(user_uuid)
            else:
                logger.error(f"{messages.error_on_getting_user}")
                # Get the user object from the Database
                user_object = await models.User.get(id=repository_object.user_id)
                if not user_object:
                    logger.error("User not found in database")
                    return JSONResponse(status_code=404, content={"message": "User not found"})

                # Get the access_token for the gitlab repository
                access_token = await Token().check_expired(user_object.id)
                # Get the model preference of the corresponding user
                model_preference = await Login().check_for_model_preference(user_object.id)

            if not access_token:
                logger.error("Failed to obtain valid access token")
                return JSONResponse(status_code=401, content={"message": "Invalid or expired token"})

            # Only proceed if we have a valid access_token
            is_vulnerability_test_enabled = repository_object.is_vulnerability_enabled
            commit_message = request_json.get('object_attributes', {}).get('last_commit', {}).get('message')
            if not commit_message:
                logger.error("Missing commit message in webhook payload")
                return JSONResponse(status_code=400, content={"message": "Invalid webhook payload"})

            logger.info(messages.fetched_commit_message)
            url_instance = request.headers.get('x-gitlab-instance')
            merge_request_id = request_json.get('object_attributes', {}).get('iid')

            if not url_instance or not merge_request_id:
                logger.error("Missing required GitLab instance URL or merge request ID")
                return JSONResponse(status_code=400, content={"message": "Missing required GitLab parameters"})

            logger.info(messages.recieved_merge_request_id_message)

        #     try:
        #         # Create the project object instance with the access token
        #         project_object = await git_object.get_project_object(url_instance, project_id, access_token,
        #                                                              constants.oauth_token)
        #         logger.info(messages.recieved_project_object_message)
        #     except GitlabAuthenticationError:
        #         logger.error(messages.authentication_error_message)
        #         return JSONResponse(status_code=401, content={"message": messages.authentication_error_message})
        #     except Exception as e:
        #         logger.error(f'{e}\t{messages.project_object_error_message}, Project id : {project_id}')
        #         return JSONResponse(status_code=400, content={"message": messages.project_object_error_message})
        #
        except Exception as e:
            logger.error(f'Failed to process user authentication: {str(e)}')
            return JSONResponse(status_code=500, content={"message": "Failed to process authentication"})
        # if project_object:
        #     try:
        #         merge_request_object = await git_object.get_merge_request_object(project_object,
        #                                                                          merge_request_id)
        #         logger.info(messages.recieved_merge_request_object_message)
        #     except Exception as e:
        #         logger.error(f'{e}\t{messages.merge_object_error_message}{merge_request_id}')
        #         return JSONResponse(status_code=400, content={"message": messages.fail_message})
        #     changes = await git_object.get_mr_changes(merge_request_object)
        #     logger.info(messages.fetched_changes_message)
        repo_params = {
            "access_token": access_token,
            "project_id": project_id,
            "merge_request_id": merge_request_id,
            'commit_message': commit_message,
            'model_preference': model_preference,
            'is_vulnerability_test_enabled':is_vulnerability_test_enabled,
            'url_instance':url_instance,
            "ignored_files": ignore_file_flattened_list
        }
        return repo_params
    else:
        return False

async def get_github_code_changes(request):
    """
    Function to get the GitHub changes
    :param request:
    :return:
    """
    logger.info(f'{messages.call_from_github}')
    request_json = await request.json()
    #Get action of the merge request
    action = request_json.get('action')
    logger.info(f'{messages.webhook_action_message}{action}')
    if action in {constants.OPEN_ACTION, constants.REOPENED_ACTION_GITHUB, constants.SYNCHRONIZED_ACTION}:
        repository = request_json.get('repository')
        project_id = repository.get('id')
        #Get the user object from the Database
        user_object = await models.User.get(web_url=request_json.get('sender').get('url'))
        repository_object = await models.Repository.filter(project_id=project_id).first()
        ignored_files_dict = repository_object.ignored_files or {}
        ignore_file_flattened_list = [
            file_path
            for branch_files in ignored_files_dict.values()
            for file_path in branch_files
        ]
        ignored_paths = set(ignore_file_flattened_list)

        #Check if the repository object is integrated for the code review from the Database
        if repository_object.is_integrated:
            merge_request_id = request_json.get('pull_request').get('number')
            #Fetch the installation id
            installation_id = (await models.UserToken.get(user_id=user_object.id)).installation_id
            #Get the access_token for the GitHub repository
            access_token = await GitHubAppToken().get_github_app_access_token(installation_id)
            #Get the model preference of the corresponding user
            model_preference = await Login().check_for_model_preference(user_object.id)
            is_vulnerability_test_enabled = repository_object.is_vulnerability_enabled
            #Create the GitHub instance with the access token

            repo_params = {
                "access_token": access_token,
                "project_id": project_id,
                "merge_request_id": merge_request_id,
                "model_preference": model_preference,
                "is_vulnerability_test_enabled": is_vulnerability_test_enabled,
                "ignored_files": ignore_file_flattened_list
            }

            # github_instance = Github(access_token)
            # project_object = github_instance.get_repo(project_id)
            # merge_request_object = project_object.get_pull(merge_request_id)
            # last_commit = merge_request_object.get_commits().reversed[0]  # Get the last commit
            # commit_message = last_commit.commit.message
            # changes = merge_request_object.get_files()
            # repo_params = {
            #     'project_object': "project_object",
            #     'merge_request_object': "merge_request_object",
            #     'commit_message': commit_message,
            #     'changes': "changes",
            #     'model_preference': model_preference,
            #     'is_vulnerability_test_enabled': is_vulnerability_test_enabled,
            # }
            return repo_params
    else:
        return False
