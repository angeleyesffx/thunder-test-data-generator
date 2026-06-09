import os


def create_folder(folder_path: str) -> None:
    if not os.path.exists(folder_path):
        os.mkdir(os.path.join(os.getcwd(), folder_path))


def delete_file(file_path: str) -> None:
    if file_exists(file_path):
        os.remove(file_path)


def file_exists(file_path: str) -> bool:
    return os.path.exists(file_path)
