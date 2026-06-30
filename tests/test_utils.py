import os
from commons.utils import create_folder, delete_file, file_exists


class TestFileExists:
    def test_returns_true_for_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("data")
        assert file_exists(str(f)) is True

    def test_returns_false_for_missing_file(self, tmp_path):
        assert file_exists(str(tmp_path / "nonexistent.txt")) is False


class TestDeleteFile:
    def test_deletes_existing_file(self, tmp_path):
        f = tmp_path / "to_delete.txt"
        f.write_text("data")
        delete_file(str(f))
        assert not f.exists()

    def test_does_not_raise_when_file_is_missing(self, tmp_path):
        delete_file(str(tmp_path / "nonexistent.txt"))


class TestCreateFolder:
    def test_creates_new_folder(self, tmp_path):
        new_dir = str(tmp_path / "new_folder")
        create_folder(new_dir)
        assert os.path.exists(new_dir)

    def test_does_not_raise_if_folder_already_exists(self, tmp_path):
        existing = str(tmp_path / "existing")
        os.mkdir(existing)
        create_folder(existing)
