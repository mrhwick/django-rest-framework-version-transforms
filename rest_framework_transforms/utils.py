from importlib import import_module
import inspect
import re
from rest_framework_transforms.transforms import BaseTransform


def get_transform_classes(transform_base=None, base_version=1, reverse=False):
    """
    Compiles a list of transform classes between the provided 'base_version' and the highest version supported.

    :param reverse: Specifies the order in which the transform classes are returned.

    Running the '.forwards()' method of the returned transform classes (in ascending order) over
    a dictionary of resource representation data will promote the dictionary from the given 'base_version' to the
    highest supported version.

    Running the '.backwards()' method of the returned transform classes (in descending order) over
    a dictionary of resource representation data will demote the dictionary from the highest supported version to the
    given 'base_version'.
    """
    module, base = transform_base.rsplit('.', 1)
    mod = import_module(module)

    transform_classes_dict = {}

    for name, transform_class in inspect.getmembers(mod):
        if name.startswith(base) and issubclass(transform_class, BaseTransform):
            transform_index_match = re.search('\d+$', name)
            if transform_index_match:
                int_transform_index = int(transform_index_match.group(0))
                if base_version < int_transform_index:
                    transform_classes_dict[int_transform_index] = transform_class

    ordered_transform_classes_list = [
        transform_classes_dict[key]
        for key
        in sorted(transform_classes_dict, reverse=reverse)
    ]

    return ordered_transform_classes_list
