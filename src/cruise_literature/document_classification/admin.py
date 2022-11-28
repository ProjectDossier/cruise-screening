from django.contrib import admin

from .models import Endpoint, MLAlgorithm, MLAlgorithmStatus, MLRequest

admin.site.register(Endpoint)
admin.site.register(MLAlgorithm)
admin.site.register(MLAlgorithmStatus)
admin.site.register(MLRequest)
