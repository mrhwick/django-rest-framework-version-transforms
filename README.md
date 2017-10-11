djangorestframework-version-transforms
======================================

[![build-status-image](https://secure.travis-ci.org/mrhwick/django-rest-framework-version-transforms.svg?branch=master)](http://travis-ci.org/mrhwick/django-rest-framework-version-transforms?branch=master)
[![pypi-version](https://img.shields.io/pypi/v/djangorestframework-version-transforms.svg)](https://pypi.python.org/pypi/djangorestframework-version-transforms)
[![read-the-docs](https://readthedocs.org/projects/django-rest-framework-version-transforms/badge/?version=latest)](http://django-rest-framework-version-transforms.readthedocs.org/en/latest/?badge=latest)

Overview
--------

A library to enable the use of delta transformations for versioning of [Django Rest Framework] API representations.

### Change is Inevitable

>Wouldn't it be nice if we only needed to design our API once?

Unfortunately for API developers, changes in API design are inevitable for many projects.
If developers cannot avoid API change, then the next best option is to manage it without sacrificing software quality.
Managing API change requires maintenance of multiple versions for our resource representations, but django rest framework sacrifices maintainability in its default versioning support.

Using the default versioning support in DRF demands that endpoint code maintain the semantic differences between version of a representation.
Forcing the responsibility of version compatibility onto the endpoint code results in endpoints that are hard to read and difficult to maintain.
The length of version compatibility boilerplate code will increase as versions are created, and so will increasingly degrade the maintainability of the endpoint code.

**There is a better way.**

### Representational Version Transforms

djangorestframework-version-transforms enables REST framework developers to remove version compatibility boilerplate from their endpoints.
Developers need only write version compatibility once per version change, in the form of version transforms.
Version transforms encapsulate the necessary changes to promote or demote a resource representation between versions.
Endpoint logic can then only concern itself with the highest (or current) version of the resource, leading to great benefits in maintainability.

Using version transforms enables API maintainers to make the necessary changes to endpoint logic that they want to make without worrying about the impact on version compatibility.

### This Library

This library aims to make maintenance of resource versions simple and intuitive for users of django rest framework by using version transforms to record incremental API changes separately from endpoint logic.

Requirements
------------

-  Python (2.7, 3.3, 3.4)
-  Django (1.6, 1.7, 1.8)
-  Django REST Framework (2.4, 3.0, 3.1)

Installation
------------

Install using ```pip```...

```bash
$ pip install djangorestframework-version-transforms
```
## Usage

### Transforms

Transforms are the classes that will be used to convert between versions of your representation during endpoint request handling.
Transforms are expected to implement two methods which enable forward (request) and backward (response) compatibility between two versions of the representation:

```python
class BaseTransform(object):
    """
    All transforms should extend 'BaseTransform', overriding the two
    methods '.forwards()' and '.backwards()' to provide forwards and backwards
    conversions between representation versions.
    """
    def forwards(self, data, request):
        """
        Converts from this transform's base version to the next version of the representation.

        :returns: Dictionary with the correct structure for the next version of the representation.
        """
        raise NotImplementedError(".forwards() must be overridden.")

    def backwards(self, data, request, instance):
        """
        Converts from the next version back to this transform's base version of the representation.

        :returns: Dictionary with the correct structure for the base version of the representation.
        """
        raise NotImplementedError(".backwards() must be overridden.")
```

To create a transform that can be used for conversion, define a subclass of `BaseTransform`:

```python
class TestModelTransform0001(BaseTransform):
    def forwards(self, data, request):
        if 'test_field_one' in data:
            data['new_test_field'] = data.get('test_field_one')
            data.pop('test_field_one')
        return data

    def backwards(self, data, request, instance):
        data['test_field_one'] = data.get('new_test_field')
        data.pop('new_test_field')
        return data
```

In this example transform, the `.forwards()` method would be used to change a v1 representation into a v2 representation by substituting a field key.
This transform indicates that it will be used to convert from v1 to v2 by appending a numerical indicator of the version it is based upon, `0001`.

To define a second transform that would enable conversion between a v2 and v3, we would simply use the same prefix with an incremented numerical indicator.

```python
class TestModelTransform0002(BaseTransform):
    def forwards(self, data, request):
        data['new_related_object_id_list'] = [1, 2, 3, 4, 5]
        return data

    def backwards(self, data, request, instance):
        data.pop('new_related_object_id_list')
        return data
```

Therefore, the second transform is indicating that it is based upon the version `0002`, and can convert forwards from a v2 to a v3 and backwards again from a v3 to a v2.
In this second example transform, the `.forwards()` method adds a required field with default values onto the representation to maintain compatibility with version 3 of the endpoint code which requires that field.

In both example transforms, the `.backwards()` method is used to convert a representation from the version above the base version down into the base version.
In the first case, this means substituting the original key back into the representation, and removing the key from the v2 representation.
In the second example, the `.backwards()` method would remove the field that is required by the v3 representation, since it was not expected in the v2 representation.


#### Uniform vs. Per-Endpoint Versioning

There are two schools of thought around versioning of resources within a REST API.
Uniform API versioning schemes increment the version of the entire API at once whenever one endpoint introduces an incompatible change.
In contrast, Per-Endpoint API versioning allows demands that a client know the version number of each resource with which they interact.

Per-Endpoint API versioning is convenient for development of the API itself, and would be the expected default for DRF-based API's.
Each endpoint likely keeps a record of versioning independently of any other endpoints.
If a uniform version number is desired, then endpoints will likely be 'pulled' forward into higher versions that are demanded by other endpoints.
This 'pulling' would be, in practice, duplication of endpoint code from an older version of some endpoint to a newer version of the same endpoint.

While per-endpoint versioning is convenient for maintenance of an API, uniform API versioning offers enormous convenience to client-side developers.

Version transforms enable either versioning scheme without code duplication.
Without additional work, per-endpoint versioning is supported.
Transforms for each endpoint simply target incremental versions of their resources.

For example, if you have two resources `User` and `Profile`:

```python
class ProfileTransform0002(BaseTransform):
    """
    Targets v2 of the profile representation.
    Will convert forwards and backwards for requests at v1.
    """

class UserTransform0002(BaseTransform):
    """
    Targets v2 of the user representation.
    Will convert forwards and backwards for requests at v1.
    """

class UserTransform0003(BaseTransform):
    """
    Targets v3 of the user representation.
    Will convert forwards and backwards for requests at v1 or v2.
    """

class UserTransform0004(BaseTransform):
    """
    Targets v4 of the user representation.
    Will convert forwards and backwards for requests at v1, v2, or v3.
    """
```

In this example, the `User` and `Profile` resources are versioned independently from one another.
`User` has a current version of `v4`, and `Profile` has a current version of `v2`.
They both define the transforms necessary to maintain older versions.

If API developers wish to support uniform versioning, this is also quite simple.
In uniform versioning schemes, the transforms are created targeting the new uniform version which will include the new representation version.

For example, if you again have two resources `User` and `Profile`:

```python
class ProfileTransform0002(BaseTransform):
    """
    Targets v2 of the profile representation.
    Will convert forwards and backwards for requests at v1.
    """

class UserTransform0003(BaseTransform):
    """
    Targets v3 of the user representation.
    Will convert forwards and backwards for requests at v1 or v2.
    """

class ProfileTransform0004(BaseTransform):
    """
    Targets v4 of the profile representation.
    Will convert forwards and backwards for requests at v1, v2, or v3.
    """

class UserTransform0004(BaseTransform):
    """
    Targets v4 of the user representation.
    Will convert forwards and backwards for requests at v1, v2, or v3.
    """
```

In the uniform versioning example, each endpoint is responsible for 'opting-in' to have a new resource version by creating a transform that targets the incrementing uniform version.
This API has a uniform version `v4`, and the `User` and `Profile` both 'opt-in' to make incompatible changes as a part of `v4` of the API.
This means that they both define a transform to maintain versions below `v4`.

Prior to the `v4` of this example API, there were other incompatible changes necessary, but only one of either `User` or `Profile` resources 'opted-in' to targeting the new uniform version.


Using these simple patterns, API developers can decide to implement the versioning scheme which is most meaningful for their projects.


### Parsers

Parsers are useful in django rest framework for defining content-types for your RESTful API resources.

Using djangorestframework-version-transforms, custom parsers can also be used to ensure that the representation parsed out of a request match the latest version of that resource.
This means that endpoint logic no longer needs to be aware of previous versions of a resource.
Whenever a request is made at a previous resource version, the inbound representation will be converted into the latest version during the parsing operation.

To make use of version transforms in parsers, define a subclass of `BaseVersioningParser`:

```python
class TestParser(BaseVersioningParser):
    media_type = 'application/vnd.test.testtype+json'
    transform_base = 'tests.test_transforms.TestModelTransform'
```

The `media_type` property must be defined, but can be defined simply as `application/json` if no custom content type is necessary.

With a `transform_base` defined, this serializer will automatically retrieve transform classes from the specified module that are prefixed with the base transform name.

In this example, the full module name is `'tests.test_transforms'`, which indicates module from which the transform classes will be loaded.
The base name in the example is `'TestModelTransform'`, which indicates the prefix for transform classes to be loaded from the module for use during conversion.

The VersioningParser will automatically run the `.forwards()` methods of each transform in ascending order, starting with the requested version.
After this operation is complete, the parser will return the representation in the latest version for handling by the endpoint logic.

### Serializers

Serializers are useful in django rest framework for returning consistent response representations to the requesting client.

Using djangorestframework-version-transforms, custom serializers can also be used to ensure that the response representation matches the representation version which the client knows how to handle.
As a response representation is being prepared for transmission back to the client, the outbound representaiton will be converted back down to the requested version during the serialization operation.

To make use of transforms in serializers, define a subclass of `BaseVersioningSerializer`:

```python
from rest_framework import serializers

# using a plain serializer
class FooSerializerV3(BaseVersioningSerializer, serializers.Serializer):
    test_field_two = serializers.CharField()

# using model serializer
class TestSerializerV3(BaseVersioningSerializer, serializers.ModelSerializer):
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
```

With a `transform_base` defined, this serializer will automatically retrieve transform classes from the specified module that are prefixed with the base name.

In this example, the module name is `'tests.test_transforms'`, which indicates the module from which the transform classes will be loaded.
The base name in the example is `'TestModelTransform'`, which indicates the prefix for transform classes to be loaded from the module for use during conversion.

The VersioningSerializer will automatically run the `.backwards()` methods of each transform in descending order, ending with the transform that has the requested version as its base.
After the conversion operation is complete, the serializer will return the representation in the version requested by the client.

## Development

### Testing

Install testing requirements.

```bash
$ pip install -r requirements.txt
```

Run with runtests.

```bash
$ ./runtests.py
```

You can also use the excellent [tox] testing tool to run the tests
against all supported versions of Python and Django. Install tox globally, and then simply run:

```bash
$ tox
```

### Documentation

To build the documentation, you’ll need to install ```mkdocs```.

```bash
$ pip install mkdocs
```

To preview the documentation:

```bash
$ mkdocs serve
Running at: http://127.0.0.1:8000/
```

To build the documentation:

```bash
$ mkdocs build
```

[Django Rest Framework]: https://github.com/tomchristie/django-rest-framework
[tox]: http://tox.readthedocs.org/en/latest/
