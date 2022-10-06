from django.test import TestCase

from .dummy import DummyClassifier


class MLTests(TestCase):
    def test_rf_algorithm(self):
        input_data = ["Test review"]
        clf = DummyClassifier()
        response = clf.predict(input_data)
        self.assertEqual("OK", response["status"])
        self.assertEqual(1, response["predictions"][0]["probability"])
        self.assertEqual(0, response["predictions"][0]["label"])
