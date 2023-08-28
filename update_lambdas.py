import os
import zipfile

import boto3

s3 = boto3.client('s3')

SOURCE_DIR = os.environ.get('LAMBDAS_SOURCE_FOLDER')

BUCKET_NAME = os.environ.get('BUCKET_NAME')

TARGET_DIR = os.environ.get('S3_LAMBDAS_DESTINATION')


def is_python_script(s3_file: str) -> bool:
    return s3_file.endswith('.py')


def create_zip_file(zip_path: str, file_path: str):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, zip_path)


def upload_file(zip_path: str):
    s3.upload_file(zip_path, BUCKET_NAME, TARGET_DIR)


def remove_file(zip_path: str):
    os.remove(zip_path)


def get_base_name(uploaded_file: str) -> str:
    return os.path.splitext(uploaded_file)[0]


def get_zip_path(base_name: str, root: str) -> str:
    return os.path.join(root, f'{base_name}.zip')


def get_file_path(root: str, uploaded_file: str) -> str:
    return os.path.join(root, uploaded_file)


def upload_lambdas():
    for root, dirs, files in os.walk(SOURCE_DIR):
        for uploaded_file in files:
            if is_python_script(uploaded_file):
                base_name = get_base_name(uploaded_file)
                file_path = get_file_path(root, uploaded_file)
                zip_path = get_zip_path(base_name, root)
                create_zip_file(zip_path, file_path)
                upload_file(zip_path)
                remove_file(zip_path)

                print(f'File: {zip_path} has been uploaded successfully')

    print('Files uploading finished')


if __name__ == '__main__':
    upload_lambdas()
