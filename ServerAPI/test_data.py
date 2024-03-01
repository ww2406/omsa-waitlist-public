import unittest
from data import compare_docs_and_notify


class MyTestCase(unittest.TestCase):
    def test_notify_wl_no_change_0(self):
        new_data = {
            '1': {
                'crn': '1',
                'wl_remaining': 0
            }
        }
        orig_data = [{
            'crn': '1',
            'wl_remaining': 0
        }]
        resp = compare_docs_and_notify(new_data, orig_data)
        self.assertListEqual([False], resp)

    def test_notify_wl_no_change_non_0(self):
        new_data = {
            '1': {
                'crn': '1',
                'wl_remaining': 5
            }
        }
        orig_data = [{
            'crn': '1',
            'wl_remaining': 5
        }]
        resp = compare_docs_and_notify(new_data, orig_data)
        self.assertListEqual([False], resp)

    def test_notify_wl_change_non_0(self):
        new_data = {
            '1': {
                'crn': '1',
                'wl_remaining': 3
            }
        }
        orig_data = [{
            'crn': '1',
            'wl_remaining': 2
        }]
        resp = compare_docs_and_notify(new_data, orig_data)
        self.assertListEqual([False], resp)

    def test_notify_wl_change_to_0(self):
        new_data = {
            '1': {
                'crn': '1',
                'wl_remaining': 0
            }
        }
        orig_data = [{
            'crn': '1',
            'wl_remaining': 3
        }]
        resp = compare_docs_and_notify(new_data, orig_data)
        self.assertListEqual([False], resp)

    def test_notify_wl_change_from_0(self):
        new_data = {
            '1': {
                'crn': '1',
                'wl_remaining': 1
            }
        }
        orig_data = [{
            'crn': '1',
            'wl_remaining': 0
        }]
        resp = compare_docs_and_notify(new_data, orig_data)
        self.assertListEqual([True], resp)


if __name__ == '__main__':
    unittest.main()
