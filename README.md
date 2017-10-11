djangorestframework-version-transforms
======================================

[![build-status-image](https://secure.travis-ci.org/mrhwick/django-rest-framework-version-transforms.svg?branch=master)](http://travis-ci.org/mrhwick/django-rest-framework-version-transforms?branch=master)
[![pypi-version](https://img.shields.io/pypi/v/djangorestframework-version-transforms.svg)](https://pypi.python.org/pypi/djangorestframework-version-transforms)
[![read-the-docs](https://readthedocs.org/projects/django-rest-framework-version-transforms/badge/?version=latest)](http://django-rest-framework-version-transforms.readthedocs.org/en/latest/?badge=latest)

# Overview

A library to enable the use of functional transforms for versioning of [Django Rest Framework] API representations.

## API Change Management - State of the Art

Unfortunately for API developers, changes in API schema are inevitable for any significant web service.

If developers cannot avoid changing their API representations, then the next best option is to manage these changes without making sacrifices to software quality. Managing API changes often requires a developer to define and maintain multiple versions of resource representations for their API. Django Rest Framework makes some code quality sacrifices in its default support for version definition.

Using the default versioning support in DRF, API developers are required to manage version differences within their endpoint code. Forcing the responsibility of version compatibility into this layer of your API increases the complexity of endpoints. As the number of supported versions increases, the length, complexity, and duplication of version compatibility boilerplate will increase, leading to ever-increasing difficulty when making subsequent changes.

We can do better than duplicating code and maintaining ever-increasing boilerplate within our APIs.

## Representation Version Transforms

`djangorestframework-version-transforms` empowers DRF users to forgo the introduction of unecessary boilerplate into their endpoint code.

Version compability is instead implemented as version transform functions that translate from one version of a resource to another. The general concept of a version transform should already be familiar to Django users, since it is derived from the frequently-used migration tool and uses similar patterns. Developers need only write version compatibility code once per version change, and need only maintain their endpoint code at the latest version.

Version transforms encapsulate the necessary changes to promote or demote a resource representation between versions, and a stack of version transforms can be used as a promotion or demotion pipeline when needed. With the correct stack of version transforms in place, endpoint logic should only be concerned with the latest (or current) version of the resource.

When backwards incompatible changes are required, the endpoint can be upgraded to work against the new version. Then a single version transform is introduced that converts between the now outdated version and the newly created "current" version that the endpoint code expects.

## Requirements

-  Python (2.7, 3.4)
-  Django (1.6, 1.7, 1.8)
-  Django REST Framework (2.4, 3.0, 3.1)

## Installation

Install using ```pip```...

```bash
$ pip install djangorestframework-version-transforms
```

## Usage

### Creating Version Transforms

Transforms are defined as python subclasses of the `BaseTransform` class. They are expected to implement two methods (`forwards` and `backwards`) which describe the necessary transformations for forward (request) and backward (response) conversion between two versions of the resource. The base version number for a transform is appended to the name.

For example:

```python
# Notice that this is a subclass of the `BaseTransform` class
class MyFirstTransform0001(BaseTransform):

    # .forwards() is used to promote request data
    def forwards(self, data, request):
        if 'test_field_one' in data:
            data['new_test_field'] = data.get('test_field_one')
            data.pop('test_field_one')
        return data

    # .backwards() is used to demote response data
    def backwards(self, data, request, instance):
        data['test_field_one'] = data.get('new_test_field')
        data.pop('new_test_field')
        return data
```

In this example transform, the `.forwards()` method would be used to change a v1 representation into a v2 representation by substituting the field key `new_test_field` for the previous key `test_field_one`. This transform indicates that it will be used to convert between v1 and v2 by appending a numerical indicator of the version it is based upon, `0001`, to the transform name. The `.backwards()` method simply does the swap operation in reverse, replacing the original field key that is expected in v1.

To define a second transform that would enable conversion between a v2 and v3, we would simply use the same prefix and increment the base version number to `0002`.

```python
# Again, subclassing `BaseTransform`.
# The postfix integer indicates the base version.
class MyFirstTransform0002(BaseTransform):

    def forwards(self, data, request):
        data['new_related_object_id_list'] = [1, 2, 3, 4, 5]
        return data

    def backwards(self, data, request, instance):
        data.pop('new_related_object_id_list')
        return data
```

In this second example transform, the `.forwards()` method adds a newly required field with some default values onto the representation. The `.backwards()` method simply removes the new field, since v2 does not require it.

### Whole-API vs. Per-Endpoint Versioning

There are two general strategies for introducing new API versions, and this library supports either version strategy.

#### Whole-API Versioning

In the Whole-API versioning strategy, any backwards-incompatible change to any endpoint within the API introduces a new API version for all endpoints. Clients are expected to maintain knowledge of the various changes particular to any resources affected by a given version change.

In this strategy, changes to resources will be bundled together as a new version alongside any unchanged resources.

Whole-API versioning offers convenience for client-side developers at runtime, since the client must only interact with one version of an API at a time. One drawback is that the client must be made to support all changes to endpoints included in each new version of the API.

##### Usage

For example, assume you have two resources `User` and `Profile`.

In the course of development, you must make several backwards incompatible changes over time:

- v1 - Some initial version of `Profile` and `User`.
- v2 - The `Profile` resource changes in some incompatible way.
- v3 - The `User` resource changes in some incompatible way.
- v4 - Both `Profile` and `User` resources change in some incompatible way at the same time.

In order to support these version changes, you would define these transforms:

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

In the Whole-API strategy, each transform targets the version to which it promotes a resource. Using this pattern, the transforms "opt in" to a particular version number.

In this example:

- `ProfileTransform0002` targets `v2`.
- `UserTransform0003` targets `v3`.
- `ProfileTransform0004` and `UserTransform0004` both target `v4`.

#### Per-Endpoint Versioning

Per-Endpoint API versioning requires a client to maintain knowledge of the various versions of each endpoint. The client will access each endpoint at its associated version, and can expect to independently change the version number for each endpoint. This allows for finer-grained control for the client to manage which resource versions with which it expects to interact.

In this strategy, changes to resources are made independently of each other. Unchanged resources stay at the same version number no matter how many new versions of other resources are created.

Per-Endpoint versioning offers convenience for client developers in that they can improve a single resource interaction at a time. One major drawback of this strategy is that the client must maintain a mapping of which resource versions are to be used at runtime.

##### Usage

For example, assume you have two resources `User` and `Profile`.

In the course of development, you must make several backwards incompatible changes over time:

Some changes to the `Profile` endpoint:

- v1 `Profile` - Some initial version of `Profile`.
- v2 `Profile` - The `Profile` resource changes in some incompatible way.

Some changes to the `User` endpoint:

- v1 `User` - Some initial version of `User`.
- v2 `User` - The `User` resource changes in some incompatible way.
- v3 `User` - The `User` resource changes in some incompatible way.
- v4 `User` - The `User` resource changes in some incompatible way.

In order to support these versions, you would define these transforms:

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

The `User` resource supports `v1`, `v2`, `v3`, and `v4`. Three transforms are defined, with each stating their targeted version after promotion by the postfix integer in their names.

The `Profile` resource supports `v1` and `v2`. One transform is defined to enable this support, and that transform states that it targets `v2` after promotion of the representation.

Using this strategy, the client-side interactions can target a different version for each of the resources independently from one another.

### Parsers

Parsers are useful in Django Rest Framework for defining content-types for your RESTful API resources.

Using this library, custom parsers can also be used to ensure that the representation parsed out of a request match the latest version of that resource. This relieves the endpoint from the burden of maintaining knowledge of previous resource versions.

When using a custom parser, inbound representations at lower-than-latest versions will be converted into the latest version during parsing.

To make use of version transforms in custom parsers, define a subclass of `BaseVersioningParser`:

```python
# Notice that this is a subclass of the provided `BaseVersioningParser`
class MyFirstVersioningParser(BaseVersioningParser):
    media_type = 'application/vnd.test.testtype+json'
    transform_base = 'my_version_transforms.MyFirstTransform'
```

The `media_type` property must be defined, but can be defined simply as `application/json` if no custom content type is desired.

The `transform_base` property can be defined for use with this library. This parser will now automatically retrieve transform classes from the specified module that are prefixed with the base transform name.

In this example, the full module name is `'my_version_transforms'`, which indicates the module from which the transform classes will be loaded. The base transform name in this example is `'MyFirstTransform'`, which indicates a prefix to be used for pattern matching to find the version transforms associated with this parser.

The VersioningParser will automatically discover the transforms from the provided module that match the given base transform name. Then, the parser will use the version being requested to identify which transform to run first. The parser then creates a pipeline from the `.forwards()` methods of each later transform in ascending order. After this promotion pipeline is complete, the parser provides the request representation at the latest version for handling by the endpoint logic.

### Serializers

Serializers are useful in Django Rest Framework for consistently returning well-formated responses to the client.

Using this library, custom serializers can also be used to ensure that responses match the version which the client originally requested. A response representation is automatically demoted back to the requested version during serialization. This again relieves endpoints from the burden of maintaining knowledge of previous versions.

To make use of transforms in serializers, define a subclass of `BaseVersioningSerializer`:

```python
from rest_framework import serializers

# using a plain serializer
class MyFirstVersioningSerializer(BaseVersioningSerializer, serializers.Serializer):
    transform_base = 'my_version_transforms.MyFirstTransform'

    test_field_two = serializers.CharField()

# using model serializer
class MyFirstVersioningSerializer(BaseVersioningSerializer, serializers.ModelSerializer):
    transform_base = 'my_version_transforms.MyFirstTransform'

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

The `transform_base` property is defined in the same manner as with parsers, using the first portions of the definition to identify from which module to load transforms, and the last part to identify the transforms to be used.

The versioning serializer will automatically discover the transforms from the provided module that match the base transform name. Then the serializer builds a pipeline of transforms to be used for demotion down to the requested version of the resource. The pipeline is run in sequence by executing the `.backwards()` methods on each transform in descending order until the requested version is reached.

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
