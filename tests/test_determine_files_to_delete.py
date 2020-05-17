from unittest import TestCase
import dobackup


class TestDetermine_files_to_delete(TestCase):
    def test_determine_files_to_delete_couple(self):
        test_base_file_name = 'testtest.zip'
        test_data = [
            ['20200501000000', test_base_file_name],
            ['20200502000000', test_base_file_name]
        ]
        expected = ['20200501000000____' + test_base_file_name]
        actual = dobackup.determine_files_to_delete(test_data, 1)
        self.assertListEqual(expected, actual)


    def test_determine_files_to_delete_several(self):
        test_base_file_name = 'testtest.zip'
        test_data = [
            ['20200501000000', test_base_file_name],
            ['20200508000000', test_base_file_name],
            ['20200515000000', test_base_file_name],
            ['20200522000000', test_base_file_name],
            ['20200529000000', test_base_file_name],
            ['20200605000000', test_base_file_name],
            ['20200612000000', test_base_file_name]
        ]
        expected = [
            '20200501000000____' + test_base_file_name,
            '20200508000000____' + test_base_file_name,
            '20200515000000____' + test_base_file_name
        ]
        actual = dobackup.determine_files_to_delete(test_data, 4)
        self.assertListEqual(expected, actual)


    def test_determine_files_to_delete_several_not_sorted(self):
        test_base_file_name = 'testtest.zip'
        test_data = [
            ['20200612000000', test_base_file_name],
            ['20200515000000', test_base_file_name],
            ['20200501000000', test_base_file_name],
            ['20200508000000', test_base_file_name],
            ['20200522000000', test_base_file_name],
            ['20200529000000', test_base_file_name],
            ['20200605000000', test_base_file_name],
        ]
        expected = [
            '20200501000000____' + test_base_file_name,
            '20200508000000____' + test_base_file_name,
            '20200515000000____' + test_base_file_name
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
            ['20200501000000', test_base_file_name],
            ['20200502000000', test_base_file_name],
            ['202005020', test_base_file_name],
            ['2020-05-02', test_base_file_name],
        ]
        expected = ['20200501000000____' + test_base_file_name]
        actual = dobackup.determine_files_to_delete(test_data, 1)
        self.assertListEqual(expected, actual)
