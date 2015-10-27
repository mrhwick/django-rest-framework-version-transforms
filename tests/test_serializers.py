from rest_framework.serializers import ModelSerializer
from rest_framework_transforms.serializers import BaseVersioningSerializer
from tests.test_models import TestModel


class TestSerializer(BaseVersioningSerializer):
    transform_base = 'test_transforms.TestModelTransform'

    class Meta:
        model = TestModel


class MatchingModelSerializer(ModelSerializer):
    class Meta:
        model = TestModel
