from rest_framework.serializers import ModelSerializer
from rest_framework_transforms.serializers import BaseVersioningSerializer
from tests.models import TestModel, TestModelV3


class TestSerializer(BaseVersioningSerializer):
    transform_base = 'tests.test_transforms.TestModelTransform'

    class Meta:
        model = TestModel


class MatchingModelSerializer(ModelSerializer):
    class Meta:
        model = TestModel


class TestSerializerV3(BaseVersioningSerializer):
    transform_base = 'tests.test_transforms.TestModelTransform'

    class Meta:
        model = TestModelV3
        fields = (
            'test_field_two',
            'test_field_three',
            'test_field_four',
            'test_field_five',
            'new_test_field',
            'new_related_object_id_list',
        )
