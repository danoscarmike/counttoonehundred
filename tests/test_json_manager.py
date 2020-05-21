import csv
import json

from distutils.util import strtobool
from unittest import TestCase

from data_management.file_manager import FileManager


class TestFileManager(TestCase):
    def setUp(self):
        self.valid_in = FileManager("test_in.json")
        self.invalid_in = FileManager("")
        self.valid_out = FileManager("test_in.json")
        self.test_dict = {"abc.xyz.com": {"title": "ABC XYZ", "is_cloud": False}}

    def test_load_json_valid(self):
        service = self.valid_in.load_json().get("test.googleapis.com")
        title = service.get("title")
        self.assertEqual("Test Service API", title)

    def test_load_json_invalid(self):
        self.assertIsNone(self.invalid_in.load_json())

    def test_write_json(self):
        test_file = self.valid_out.write_file(self.test_dict)
        with open("test_out.json", "r") as test_file:
            test_json = json.load(test_file)
        test_service = test_json.get("abc.xyz.com")
        test_title = test_service.get("title")
        self.assertEqual("ABC XYZ", test_title)

    def test_write_csv(self):
        test_file = self.valid_out.write_file(self.test_dict)
        with open("test_out.csv", "r") as test_file:
            line_reader = csv.reader(test_file, delimiter=",")
            # skip header
            next(line_reader)
            test_csv = next(line_reader)
        self.assertEqual("ABC XYZ", test_csv[0])
        self.assertEqual("abc.xyz.com", test_csv[1])
        self.assertFalse(strtobool(test_csv[2]))
