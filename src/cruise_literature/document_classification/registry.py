from document_classification.models import Endpoint, MLAlgorithm, MLAlgorithmStatus

from document_classification.classifiers.dummy import DummyClassifier


class MLRegistry:
    def __init__(self):
        _endpoints = Endpoint.objects.all()
        ml_algorithms = MLAlgorithm.objects.all()
        # TODO: replace endpoints values from hardcoded DummyClassifier to a DB pickle
        self.endpoints = {
            ml_algorithm.id: DummyClassifier() for ml_algorithm in ml_algorithms
        }

    def add_algorithm(
        self,
        endpoint_name,
        algorithm_object,
        algorithm_name,
        algorithm_status,
        algorithm_version,
        owner,
        algorithm_description,
        algorithm_code,
    ):
        # get endpoint
        endpoint, _ = Endpoint.objects.get_or_create(name=endpoint_name, owner=owner)

        # get algorithm
        database_object, algorithm_created = MLAlgorithm.objects.get_or_create(
            name=algorithm_name,
            description=algorithm_description,
            code=algorithm_code,
            version=algorithm_version,
            owner=owner,
            parent_endpoint=endpoint,
        )
        if algorithm_created:
            status = MLAlgorithmStatus(
                status=algorithm_status,
                created_by=owner,
                parent_mlalgorithm=database_object,
                active=True,
            )
            status.save()

        # add to registry
        self.endpoints[database_object.id] = algorithm_object
