from rest_framework_transforms.parsers import BaseVersioningParser


class TestParser(BaseVersioningParser):
    media_type = 'application/vnd.test.testtype+json'
    transform_base = 'test_transforms.TestModelTransform'
