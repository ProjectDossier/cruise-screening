import unittest

from flaskr.classifiers.dummy import DummyClassifier


class MLTests(unittest.TestCase):
    def test_dummy_algorithm(self):
        input_data = ["Test review"]
        clf = DummyClassifier()
        response = clf.predict(input_data)
        assert "OK" == response["status"]
        assert 1 == response["predictions"][0]["probability"]
        assert response["predictions"][0]["label"] in [0, 1]
