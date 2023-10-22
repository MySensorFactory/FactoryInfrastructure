import os
import zipfile

import boto3

s3 = boto3.client('s3')

LAMBDA_SOURCE_DIR = os.environ.get('LAMBDAS_SOURCE_FOLDER')

BUCKET_NAME = os.environ.get('BUCKET_NAME')

LAMBDA_S3_TARGET_DIR = os.environ.get('S3_LAMBDAS_DESTINATION')

CICD_FUNCTIONS_SOURCE_DIR = os.environ.get('CICD_FUNCTIONS_SOURCE_DIR')

CICD_FUNCTIONS_S3_TARGET_DIR = os.environ.get('S3_CICD_FUNCTIONS_DESTINATION')

def is_python_script(s3_file: str) -> bool:
    return s3_file.endswith('.py')


def create_zip_file(zip_path: str, file_path: str):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        arch_path = os.path.split(file_path)[-1]
        if file_path.endswith('commons.py'):
            zipf.mkdir('python')
            arch_path = 'python/' + arch_path
        zipf.write(file_path, arch_path)


def upload_file(zip_path: str, bucket_name: str, dest_file: str):
    s3.upload_file(zip_path, bucket_name, dest_file)


def remove_file(zip_path: str):
    os.remove(zip_path)


def get_base_name(uploaded_file: str) -> str:
    return os.path.splitext(uploaded_file)[0]


def get_zip_path(base_name: str, root: str) -> str:
    return os.path.join(root, f'{base_name}.zip')


def get_file_path(root: str, uploaded_file: str) -> str:
    return os.path.join(root, uploaded_file)


def get_s3_target_filename(zip_path: str, s3_target_dir) -> str:
    return s3_target_dir + '/' + os.path.split(zip_path)[-1]


def upload_other_file(root: str,
                      s3_target_dir: str,
                      bucket_name: str,
                      uploaded_file: str) -> tuple[str, str]:
    file_path = get_file_path(root, uploaded_file)
    dest_file = get_s3_target_filename(
        zip_path=file_path,
        s3_target_dir=s3_target_dir
    )
    upload_file(zip_path=file_path,
                bucket_name=bucket_name,
                dest_file=dest_file)
    return dest_file, file_path


def upload_script_as_zip(root: str,
                         bucket_name: str,
                         uploaded_file: str,
                         s3_target_dir: str) -> tuple[str, str]:
    base_name = get_base_name(uploaded_file)
    file_path = get_file_path(root, uploaded_file)
    zip_path = get_zip_path(base_name, root)
    create_zip_file(zip_path, file_path)
    dest_file = get_s3_target_filename(
        zip_path=zip_path,
        s3_target_dir=s3_target_dir
    )
    upload_file(
        zip_path=zip_path,
        bucket_name=bucket_name,
        dest_file=dest_file
    )
    remove_file(zip_path)
    return dest_file, file_path


def upload_files_from_dir_recursively(source_dir: str,
                                      bucket_name: str,
                                      s3_target_dir: str,
                                      should_treat_script_as_lambda: bool = True
                                      ):
    for root, dirs, files in os.walk(source_dir):
        for uploaded_file in files:
            if is_python_script(uploaded_file) and should_treat_script_as_lambda:
                dest_file, file_path = upload_script_as_zip(
                    root=root,
                    bucket_name=bucket_name,
                    uploaded_file=uploaded_file,
                    s3_target_dir=s3_target_dir
                )
            else:
                dest_file, file_path = upload_other_file(root=root,
                                                         s3_target_dir=s3_target_dir,
                                                         bucket_name=bucket_name,
                                                         uploaded_file=uploaded_file)
            print(f'File: {file_path} has been uploaded successfully to {bucket_name}/{dest_file}')

    print('Files uploading finished')


if __name__ == '__main__':
    upload_files_from_dir_recursively(
        source_dir=LAMBDA_SOURCE_DIR,
        bucket_name=BUCKET_NAME,
        s3_target_dir=LAMBDA_S3_TARGET_DIR
    )
    upload_files_from_dir_recursively(
        source_dir=CICD_FUNCTIONS_SOURCE_DIR,
        bucket_name=BUCKET_NAME,
        s3_target_dir=CICD_FUNCTIONS_S3_TARGET_DIR,
        should_treat_script_as_lambda=False
    )
