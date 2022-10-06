import inspect

from django.test import TestCase

from .classifiers.dummy import DummyClassifier
from .registry import MLRegistry
from users.models import User
from django.test import TestCase
from rest_framework.test import APIClient


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
