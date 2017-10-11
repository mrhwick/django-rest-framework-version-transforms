from rest_framework import serializers
from rest_framework_transforms.serializers import BaseVersioningSerializer
from tests.models import TestModel, TestModelV3


class TestModelSerializer(BaseVersioningSerializer, serializers.ModelSerializer):
    transform_base = 'tests.test_transforms.TestModelTransform'

    class Meta:
        model = TestModel
        exclude = tuple()


class MatchingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        exclude = tuple()


class TestModelSerializerV3(BaseVersioningSerializer, serializers.ModelSerializer):
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


class TestSerializer(BaseVersioningSerializer, serializers.Serializer):
    transform_base = 'tests.test_transforms.TestModelTransform'

    test_field_one = serializers.CharField()
    test_field_two = serializers.CharField()
    test_field_three = serializers.CharField()
    test_field_four = serializers.CharField()
    test_field_five = serializers.CharField()


class MatchingSerializer(serializers.Serializer):
    test_field_one = serializers.CharField()
    test_field_two = serializers.CharField()
    test_field_three = serializers.CharField()
    test_field_four = serializers.CharField()
    test_field_five = serializers.CharField()


class TestSerializerV3(BaseVersioningSerializer, serializers.Serializer):
    transform_base = 'tests.test_transforms.TestModelTransform'

    test_field_two = serializers.CharField()
    test_field_three = serializers.CharField()
    test_field_four = serializers.CharField()
    test_field_five = serializers.CharField()
    new_test_field = serializers.CharField()
    new_related_object_id_list = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
