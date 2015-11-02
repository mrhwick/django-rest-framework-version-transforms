import io
import json
from unittest import TestCase
import pytest
from rest_framework.parsers import JSONParser
from rest_framework_transforms.utils import get_transform_classes

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
from rest_framework.test import APIRequestFactory
from rest_framework_transforms.exceptions import TransformBaseNotDeclaredException
from tests.models import TestModel, TestModelV3
from tests.test_parsers import TestParser
from tests.test_serializers import TestSerializer, MatchingModelSerializer, TestSerializerV3
from tests.test_transforms import TestModelTransform0002, TestModelTransform0003


@patch('rest_framework_transforms.utils.inspect.getmembers')
@patch('rest_framework_transforms.utils.import_module')
class GetTransformClassesUnitTests(TestCase):
    def test_calls_inspect_getmembers_with_module(self, import_module_mock, getmembers_mock):
        get_transform_classes(transform_base='some_package.some_module.SomeTransformBase')
        import_module_mock.assert_called_once_with('some_package.some_module')
        getmembers_mock.assert_called_once_with(import_module_mock.return_value)

    def test_adds_transforms_to_list(self, import_module_mock, getmembers_mock):
        getmembers_mock.return_value = {
            'TestModelTransform0002': TestModelTransform0002,
            'TestModelTransform0003': TestModelTransform0003,
        }.items()
        returned_classes = get_transform_classes(
            transform_base='some_package.some_module.TestModelTransform',
        )
        self.assertEqual(TestModelTransform0002, returned_classes[0])
        self.assertEqual(TestModelTransform0003, returned_classes[1])
        self.assertEqual(2, len(returned_classes))

    def test_adds_transforms_to_list_in_reverse_order(self, import_module_mock, getmembers_mock):
        getmembers_mock.return_value = {
            'TestModelTransform0002': TestModelTransform0002,
            'TestModelTransform0003': TestModelTransform0003,
        }.items()
        returned_classes = get_transform_classes(
            transform_base='some_package.some_module.TestModelTransform',
            reverse=True,
        )
        self.assertEqual(TestModelTransform0002, returned_classes[1])
        self.assertEqual(TestModelTransform0003, returned_classes[0])
        self.assertEqual(2, len(returned_classes))

    def test_adds_only_transforms_matching_base_to_list(self, import_module_mock, getmembers_mock):
        getmembers_mock.return_value = {
            'TestModelTransform0002': TestModelTransform0002,
            'AnotherModelTransform0002': TestModelTransform0003,
        }.items()
        returned_classes = get_transform_classes(
            transform_base='some_package.some_module.TestModelTransform',
        )
        self.assertEqual(TestModelTransform0002, returned_classes[0])
        self.assertNotIn(TestModelTransform0003, returned_classes)
        self.assertEqual(1, len(returned_classes))

    def test_adds_only_transforms_above_base_version_number_to_list(self, import_module_mock, getmembers_mock):
        getmembers_mock.return_value = {
            'TestModelTransform0002': TestModelTransform0002,
            'TestModelTransform0003': TestModelTransform0003,
        }.items()
        returned_classes = get_transform_classes(
            transform_base='some_package.some_module.TestModelTransform',
            base_version=2,
        )
        self.assertNotIn(TestModelTransform0002, returned_classes)
        self.assertEqual(TestModelTransform0003, returned_classes[0])
        self.assertEqual(1, len(returned_classes))


class VersioningParserUnitTests(TestCase):
    def setUp(self):
        self.request = APIRequestFactory().get('')
        self.request.version = 1
        self.parser = TestParser()
        self.json_string = json.dumps(
            {
                'test_field_one': 'value_one',
                'test_field_two': 'value_two',
                'test_field_three': 'value_three',
                'test_field_four': 'value_four',
                'test_field_five': 'value_five',
            },
        )
        self.json_string_data = io.BytesIO(str.encode(self.json_string))

    def test_parse_raises_error_when_no_transform_base_specified(self):
        self.parser.transform_base = None
        with self.assertRaises(TransformBaseNotDeclaredException):
            self.parser.parse(stream=None)

    def test_unversioned_request_returns_default_parsed_data(self):
        self.request = APIRequestFactory().get('')
        data_dict = self.parser.parse(
            stream=self.json_string_data,
            media_type='application/vnd.test.testtype+json',
            parser_context={
                'request': self.request,
            },
        )
        self.json_string_data = io.BytesIO(str.encode(self.json_string))
        default_data_dict = JSONParser().parse(
            stream=self.json_string_data,
            media_type='application/vnd.test.testtype+json',
            parser_context={
                'request': self.request,
            },
        )
        self.assertEqual(data_dict, default_data_dict)

    @patch('rest_framework_transforms.parsers.get_transform_classes')
    def test_parse_gets_transform_classes_with_version_specified(self, get_transform_classes_mock):
        self.parser.parse(
            stream=self.json_string_data,
            media_type='application/vnd.test.testtype+json',
            parser_context={
                'request': self.request,
            },
        )
        self.assertTrue(get_transform_classes_mock.called)
        get_transform_classes_mock.assert_called_once_with(
            'tests.test_transforms.TestModelTransform',
            base_version=self.request.version,
            reverse=False,
        )

    @patch('rest_framework_transforms.parsers.get_transform_classes')
    def test_parse_doesnt_get_transform_classes_with_no_version_specified(self, get_transform_classes_mock):
        self.request = APIRequestFactory().get('')
        self.parser.parse(
            stream=self.json_string_data,
            media_type='application/vnd.test.testtype+json',
            parser_context={
                'request': self.request,
            },
        )
        self.assertFalse(get_transform_classes_mock.called)

    @patch('rest_framework_transforms.parsers.get_transform_classes')
    def test_parse_calls_forwards_on_transform_classes(self, get_transform_classes_mock):
        transform_one = MagicMock()
        transform_two = MagicMock()
        get_transform_classes_mock.return_value = [
            transform_one,
            transform_two,
        ]

        self.parser.parse(
            stream=self.json_string_data,
            media_type='application/vnd.test.testtype+json',
            parser_context={
                'request': self.request,
            },
        )

        self.json_string_data = io.BytesIO(str.encode(self.json_string))
        self.assertTrue(transform_one.return_value.forwards.called)
        transform_one.return_value.forwards.assert_called_once_with(
            data=JSONParser().parse(
                stream=self.json_string_data,
                media_type='application/vnd.test.testtype+json',
                parser_context={
                    'request': self.request,
                },
            ),
            request=self.request,
        )

        self.assertTrue(transform_two.return_value.forwards.called)
        transform_two.return_value.forwards.assert_called_once_with(
            data=transform_one.return_value.forwards.return_value,
            request=self.request,
        )


class VersioningParserIntegrationTests(TestCase):
    def setUp(self):
        self.request = APIRequestFactory().get('')
        self.request.version = 1
        self.parser = TestParser()
        self.json_string = json.dumps(
            {
                'test_field_one': 'value_one',
                'test_field_two': 'value_two',
                'test_field_three': 'value_three',
                'test_field_four': 'value_four',
                'test_field_five': 'value_five',
            },
        )
        self.json_string_data = io.BytesIO(str.encode(self.json_string))

    def test_parsing_does_forward_conversion_v1_to_v3(self):
        data_dict = self.parser.parse(
            stream=self.json_string_data,
            media_type='application/vnd.test.testtype+json',
            parser_context={
                'request': self.request,
            },
        )
        self.assertTrue('new_test_field' in data_dict)
        self.assertEqual(data_dict['new_test_field'], 'value_one')
        self.assertTrue('new_related_object_id_list' in data_dict)
        self.assertEqual(data_dict['new_related_object_id_list'], [1, 2, 3, 4, 5])


class VersioningSerializerUnitTests(TestCase):
    def setUp(self):
        self.request = APIRequestFactory().get('')
        self.request.version = 1
        self.serializer = TestSerializer(context={'request': self.request})

    def test_to_representation_raises_error_when_no_transform_base_specified_with_instance(self):
        self.serializer.transform_base = None
        with self.assertRaises(TransformBaseNotDeclaredException):
            self.serializer.to_representation(instance=TestModel())

    def test_to_representation_raises_error_when_no_transform_base_specified_without_instance(self):
        self.serializer.transform_base = None
        with self.assertRaises(TransformBaseNotDeclaredException):
            self.serializer.to_representation(instance=None)

    @patch('rest_framework_transforms.serializers.get_transform_classes')
    def test_to_representation_gets_transform_classes_with_instance(self, get_transform_classes_mock):
        self.serializer.to_representation(instance=TestModel())
        self.assertTrue(get_transform_classes_mock.called)
        get_transform_classes_mock.assert_called_once_with(
            'tests.test_transforms.TestModelTransform',
            base_version=self.request.version,
            reverse=True,
        )

    @patch('rest_framework_transforms.serializers.get_transform_classes')
    def test_to_representation_calls_backwards_on_transform_classes_with_instance(self, get_transform_classes_mock):
        instance = TestModel(
            test_field_one='test_one',
            test_field_two='test_two',
            test_field_three='test_three',
            test_field_four='test_four',
            test_field_five='test_five',
        )
        transform_one = MagicMock()
        transform_two = MagicMock()
        get_transform_classes_mock.return_value = [
            transform_one,
            transform_two,
        ]

        self.serializer.to_representation(instance=instance)

        self.assertTrue(transform_one.return_value.backwards.called)
        transform_one.return_value.backwards.assert_called_once_with(
            MatchingModelSerializer().to_representation(instance),
            self.request,
            instance,
        )
        self.assertTrue(transform_two.return_value.backwards.called)
        transform_two.return_value.backwards.assert_called_once_with(
            transform_one.return_value.backwards.return_value,
            self.request,
            instance,
        )

    def test_to_representation_returns_default_serialization_if_no_request(self):
        self.serializer = TestSerializer(context={'request': None})
        instance = TestModel(
            test_field_one='test_one',
            test_field_two='test_two',
            test_field_three='test_three',
            test_field_four='test_four',
            test_field_five='test_five',
        )
        data = self.serializer.to_representation(instance=instance)
        self.assertEqual(data, MatchingModelSerializer().to_representation(instance))

    def test_to_representation_returns_default_serialization_if_no_request_version(self):
        self.request = APIRequestFactory().get('')
        self.serializer = TestSerializer(context={'request': self.request})
        instance = TestModel(
            test_field_one='test_one',
            test_field_two='test_two',
            test_field_three='test_three',
            test_field_four='test_four',
            test_field_five='test_five',
        )
        data = self.serializer.to_representation(instance=instance)
        self.assertEqual(data, MatchingModelSerializer().to_representation(instance))

    def test_to_representation_returns_empty_serialization_if_no_instance(self):
        data = self.serializer.to_representation(instance=None)
        self.assertEqual(data, MatchingModelSerializer().to_representation(None))

    @patch('rest_framework_transforms.serializers.get_transform_classes')
    def test_to_representation_doesnt_get_transform_classes_without_instance(self, get_transform_classes_mock):
        self.serializer.to_representation(instance=None)
        self.assertFalse(get_transform_classes_mock.called)

    @patch('rest_framework_transforms.serializers.get_transform_classes')
    def test_to_representation_doesnt_get_transform_classes_without_version(self, get_transform_classes_mock):
        self.request = APIRequestFactory().get('')
        self.serializer = TestSerializer(context={'request': self.request})
        self.serializer.to_representation(instance=TestModel())
        self.assertFalse(get_transform_classes_mock.called)


class VersioningSerializerIntegrationTests(TestCase):
    def setUp(self):
        self.request = APIRequestFactory().get('')
        self.request.version = 1
        self.serializer = TestSerializerV3(context={'request': self.request})
        self.instance = TestModelV3.objects.create(
            test_field_two='value_two',
            test_field_three='value_three',
            test_field_four='value_four',
            test_field_five='value_five',
            new_test_field='SOME TEST VALUE',
        )
        self.instance.new_related_object_id_list.create()
        self.instance.new_related_object_id_list.create()
        self.instance.new_related_object_id_list.create()
        self.instance.new_related_object_id_list.create()
        self.instance = TestModelV3.objects.get(id=self.instance.id)

    @pytest.mark.django_db
    def test_serialization_does_backwards_conversion_v3_to_v1(self):
        data = self.serializer.to_representation(instance=self.instance)
        self.assertTrue('test_field_one' in data)
        self.assertEqual(data['test_field_one'], 'SOME TEST VALUE')
        self.assertFalse('new_related_object_id_list' in data)

    @pytest.mark.django_db
    def test_serialization_does_backwards_conversion_v3_to_v2(self):
        self.request.version = 2
        self.serializer = TestSerializerV3(context={'request': self.request})
        data = self.serializer.to_representation(instance=self.instance)
        self.assertFalse('test_field_one' in data)
        self.assertFalse('new_related_object_id_list' in data)

    @pytest.mark.django_db
    def test_serialization_does_nothing_on_v3_to_v3(self):
        self.request.version = 3
        self.serializer = TestSerializerV3(context={'request': self.request})
        data = self.serializer.to_representation(instance=self.instance)
        self.assertFalse('test_field_one' in data)
        self.assertTrue('new_related_object_id_list' in data)
        self.assertEqual(data['new_related_object_id_list'], [1, 2, 3, 4])
