import os
import zipfile

import boto3

s3 = boto3.client('s3')

SOURCE_DIR = 'lambda_functions'

BUCKET_NAME = 'factory-ci-cd'

TARGET_DIR = 'applications/lambda'


def is_python_script(s3_file: str) -> bool:
    return s3_file.endswith('.py')


def create_zip_file(zip_path: str, file_path: str):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, zip_path)


def upload_file(zip_path: str, dest_file: str):
    s3.upload_file(zip_path, BUCKET_NAME, dest_file)


def remove_file(zip_path: str):
    os.remove(zip_path)


def get_base_name(uploaded_file: str) -> str:
    return os.path.splitext(uploaded_file)[0]


def get_zip_path(base_name: str, root: str) -> str:
    return os.path.join(root, f'{base_name}.zip')


def get_file_path(root: str, uploaded_file: str) -> str:
    return os.path.join(root, uploaded_file)


def get_target_filename(zip_path: str) -> str:
    return TARGET_DIR + '/' + os.path.split(zip_path)[-1]


def upload_other_file(root: str, uploaded_file: str) -> tuple[str, str]:
    file_path = get_file_path(root, uploaded_file)
    dest_file = get_target_filename(file_path)
    upload_file(file_path, dest_file)
    return dest_file, file_path


def upload_script_as_zip(root: str, uploaded_file: str) -> tuple[str, str]:
    base_name = get_base_name(uploaded_file)
    file_path = get_file_path(root, uploaded_file)
    zip_path = get_zip_path(base_name, root)
    create_zip_file(zip_path, file_path)
    dest_file = get_target_filename(zip_path)
    upload_file(zip_path, dest_file)
    remove_file(zip_path)
    return dest_file, file_path


def upload_lambdas():
    for root, dirs, files in os.walk(SOURCE_DIR):
        for uploaded_file in files:
            if is_python_script(uploaded_file):
                dest_file, file_path = upload_script_as_zip(root, uploaded_file)
            else:
                dest_file, file_path = upload_other_file(root, uploaded_file)
            print(f'File: {file_path} has been uploaded successfully to {BUCKET_NAME}/{dest_file}')

    print('Files uploading finished')


if __name__ == '__main__':
    upload_lambdas()
