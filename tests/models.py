from django.db import models
from django.db.models import Model


class TestModel(Model):
    test_field_one = models.CharField(max_length=20)
    test_field_two = models.CharField(max_length=20)
    test_field_three = models.CharField(max_length=20)
    test_field_four = models.CharField(max_length=20)
    test_field_five = models.CharField(max_length=20)


class TestModelV3(Model):
    test_field_two = models.CharField(max_length=20)
    test_field_three = models.CharField(max_length=20)
    test_field_four = models.CharField(max_length=20)
    test_field_five = models.CharField(max_length=20)
    new_test_field = models.CharField(max_length=20)


class OtherTestModel(Model):
    some_foreign_key = models.ForeignKey(TestModelV3, related_name='new_related_object_id_list')
