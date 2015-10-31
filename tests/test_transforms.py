from rest_framework_transforms.transforms import BaseTransform


class TestModelTransform0002(BaseTransform):
    def forwards(self, data, request):
        if 'test_field_one' in data:
            data['new_test_field'] = data.get('test_field_one')
            data.pop('test_field_one')
        return data

    def backwards(self, data, request, instance):
        data['test_field_one'] = data.get('new_test_field')
        data.pop('new_test_field')
        return data


class TestModelTransform0003(BaseTransform):
    def forwards(self, data, request):
        data['new_related_object_id_list'] = [1, 2, 3, 4, 5]
        return data

    def backwards(self, data, request, instance):
        data.pop('new_related_object_id_list')
        return data
