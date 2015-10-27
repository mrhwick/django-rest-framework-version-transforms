from django.db import models
from django.db.models import Model


class TestModel(Model):
    test_field_one = models.CharField()
    test_field_two = models.CharField()
    test_field_three = models.CharField()
    test_field_four = models.CharField()
    test_field_five = models.CharField()
