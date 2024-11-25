import inspect

from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from src.backend.ml_api.classifiers.dummy import DummyClassifier
from src.backend.ml_api.registry import MLRegistry


class MLRegistryTests(TestCase):
    def test_registry(self):
        user = User.objects.create_user("myuser", "myemail@test.com", "test_password")
        registry = MLRegistry()
        self.assertEqual(len(registry.endpoints), 0)
        endpoint_name = "text_classification"
        algorithm_object = DummyClassifier()
        algorithm_name = "dummy classifier"
        algorithm_status = "production"
        algorithm_version = "0.0.1"
        algorithm_owner = user  # TODO: replace with user
        algorithm_description = "Dummy classifier always predicting '1'."
        algorithm_code = inspect.getsource(DummyClassifier)

        # add to registry
        registry.add_algorithm(
            endpoint_name,
            algorithm_object,
            algorithm_name,
            algorithm_status,
            algorithm_version,
            algorithm_owner,
            algorithm_description,
            algorithm_code,
        )

        # there should be one endpoint available
        self.assertEqual(len(registry.endpoints), 1)


class EndpointTests(TestCase):
    def test_predict_view(self):
        user = User.objects.create_user("myuser", "myemail@test.com", "test_password")
        client = APIClient()
        input_data = ["This text should be included"]
        classifier_url = "/api/v1/text_classification/predict"
        response = client.post(classifier_url, input_data, format="json")
        self.assertEqual(response.status_code, 404)
