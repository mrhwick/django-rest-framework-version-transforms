# -*- coding: utf-8 -*-

from rest_framework import serializers
from rest_framework_transforms.exceptions import TransformBaseNotDeclaredException
from rest_framework_transforms.utils import get_transform_classes


class BaseVersioningSerializer(serializers.ModelSerializer):
    """
    A base class for serializers that automatically demote resource representations
    according to provided transform classes for the resource.
    """
    transform_base = None

    def to_representation(self, instance):
        """
        Serializes the outgoing data as JSON and executes any available version transforms in backwards
        order against the serialized representation to convert the highest supported version into the
        requested version of the resource.
        """
        if not self.transform_base:
            raise TransformBaseNotDeclaredException("VersioningParser cannot correctly promote incoming resources with no transform classes.")

        data = super(BaseVersioningSerializer, self).to_representation(instance)
        if instance:
            request = self.context.get('request')

            if request and hasattr(request, 'version'):
                # demote data until we've run the transform just above the requested version

                for transform in get_transform_classes(self.transform_base, base_version=request.version, reverse=True):
                    data = transform().backwards(data, request, instance)

        return data
