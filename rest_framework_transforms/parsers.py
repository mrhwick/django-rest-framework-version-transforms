# -*- coding: utf-8 -*-

from rest_framework.parsers import JSONParser
from rest_framework_transforms.exceptions import TransformBaseNotDeclaredException
from rest_framework_transforms.utils import get_transform_classes


class BaseVersioningParser(JSONParser):
    """
    A base class for parsers that automatically promote resource representations
    according to provided transform classes for that resource.
    """
    media_type = None
    transform_base = None

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as JSON and executes any available version transforms against the
        parsed representation to convert the requested version of this content type into the
        highest supported version of the content type.

        :returns: A dictionary of upconverted request data in the most recent supported version of the content type.
        """
        if not self.transform_base:
            raise TransformBaseNotDeclaredException("VersioningParser cannot correctly promote incoming resources with no transform classes.")

        json_data_dict = super(BaseVersioningParser, self).parse(stream, media_type, parser_context)
        request = parser_context['request']

        if hasattr(request, 'version'):
            for transform in get_transform_classes(self.transform_base, base_version=request.version, reverse=False):
                json_data_dict = transform().forwards(data=json_data_dict, request=request)

        return json_data_dict
