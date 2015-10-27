

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
