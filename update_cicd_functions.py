import os

import boto3

s3 = boto3.client('s3')

SOURCE_DIR = os.environ.get('CICD_FUNCTIONS_SOURCE_FOLDER')

BUCKET_NAME = os.environ.get('BUCKET_NAME')

TARGET_DIR = os.environ.get('S3_CICD_FUNCTIONS_DESTINATION')


def upload_file(zip_path: str, dest_file: str):
    s3.upload_file(zip_path, BUCKET_NAME, dest_file)


def get_file_path(root: str, uploaded_file: str) -> str:
    return os.path.join(root, uploaded_file)


def get_target_filename(zip_path: str) -> str:
    return TARGET_DIR + '/' + os.path.split(zip_path)[-1]


def upload_cicd_tool(root: str, uploaded_file: str) -> tuple[str, str]:
    file_path = get_file_path(root, uploaded_file)
    dest_file = get_target_filename(file_path)
    upload_file(file_path, dest_file)
    return dest_file, file_path


def upload_lambdas():
    for root, dirs, files in os.walk(SOURCE_DIR):
        for uploaded_file in files:
            dest_file, file_path = upload_cicd_tool(root, uploaded_file)
            print(f'File: {file_path} has been uploaded successfully to {BUCKET_NAME}/{dest_file}')

    print('Files uploading finished')


if __name__ == '__main__':
    upload_lambdas()
