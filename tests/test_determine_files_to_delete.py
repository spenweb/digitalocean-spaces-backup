from unittest import TestCase
import dobackup

class TestDetermine_files_to_delete(TestCase):
    def test_determine_files_to_delete_couple(self):
        test_base_file_name = 'testtest.zip'
        test_data = [
            ['20200501', test_base_file_name],
            ['20200502', test_base_file_name]
        ]
        expected = ['20200501____' + test_base_file_name]
        actual = dobackup.determine_files_to_delete(test_data, 1)
        self.assertListEqual(expected, actual)


    def test_determine_files_to_delete_several(self):
        test_base_file_name = 'testtest.zip'
        test_data = [
            ['20200501', test_base_file_name],
            ['20200508', test_base_file_name],
            ['20200515', test_base_file_name],
            ['20200522', test_base_file_name],
            ['20200529', test_base_file_name],
            ['20200605', test_base_file_name],
            ['20200612', test_base_file_name]
        ]
        expected = [
            '20200501____' + test_base_file_name,
            '20200508____' + test_base_file_name,
            '20200515____' + test_base_file_name
        ]
        actual = dobackup.determine_files_to_delete(test_data, 4)
        self.assertListEqual(expected, actual)


    def test_determine_files_to_delete_several_not_sorted(self):
        test_base_file_name = 'testtest.zip'
        test_data = [
            ['20200612', test_base_file_name],
            ['20200515', test_base_file_name],
            ['20200501', test_base_file_name],
            ['20200508', test_base_file_name],
            ['20200522', test_base_file_name],
            ['20200529', test_base_file_name],
            ['20200605', test_base_file_name],
        ]
        expected = [
            '20200501____' + test_base_file_name,
            '20200508____' + test_base_file_name,
            '20200515____' + test_base_file_name
        ]
        actual = dobackup.determine_files_to_delete(test_data, 4)
        self.assertListEqual(expected, actual)

    def test_determine_files_to_delete_couple_bad_time_prefix(self):
        """
        Should skip over badly formatted time prefixes.
        :return:
        """
        test_base_file_name = 'testtest.zip'
        test_data = [
            ['20200501', test_base_file_name],
            ['20200502', test_base_file_name],
            ['202005020', test_base_file_name],
            ['2020-05-02', test_base_file_name],
        ]
        expected = ['20200501____' + test_base_file_name]
        actual = dobackup.determine_files_to_delete(test_data, 1)
        self.assertListEqual(expected, actual)
