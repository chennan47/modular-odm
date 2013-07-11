from fields import Field
from fields.ListField import ListField

import copy

class SchemaObject(object):

    # Initialize _collections table. This variable maps lower-cased class names
    # to class references.
    _collections = {}

    @classmethod
    def register(cls, **kwargs):
        cls._collections[cls.__name__.lower()] = cls

    @classmethod
    def get_collection(cls, name):
        return cls._collections[name.lower()]

    @property
    def _primary_key(self):
        return getattr(self, self._primary_name)

    @_primary_key.setter
    def _primary_key(self, value):
        setattr(self, self._primary_name, value)

    def to_storage(self, original=False):
        # if original:
        #     d = {field_name:field_object.to_storage(field_object.get_original(self)) for field_name,field_object in self._fields.items()}
        # else:
        d = {field_name:field_object.to_storage(field_object.__get__(self, None)) for field_name,field_object in self._fields.items()}
        if self._backrefs:
            d['_backrefs'] = self._backrefs
        return d

    def _process_and_get_fields(self):
        """ Prepare and retrieve schema fields. """
        # TODO: This checks all class-level fields whenever a new record is
        # instantiated. Is this the expected behavior?
        #
        out = {}
        found_primary = False
        for k,v in self.__class__.__dict__.items():

            if not isinstance(v, Field):
                continue

            v._parent = self

            # Check for primary key
            if v._is_primary:
                if not found_primary:
                    self._primary_name = k
                    found_primary = True
                else:
                    raise Exception('Multiple keys are not supported')

            # Check for list
            if v._list:
                # Create ListField instance
                # TODO: Should this also pass kwargs? I *think* this setup means that,
                # for example, ListField defaults are never set by the user.
                v = ListField(v) # v is the field that is being list-ified
                # Replace class-level descriptor with ListField
                setattr(self.__class__, k, v)

            out[k] = v

        return out

    def __init__(self, **kwargs):

        self._is_loaded = kwargs.pop('_is_loaded', False)

        # Set _primary_name to '_id' by default
        self._primary_name = '_id'

        # Store dict of class-level Field instances
        self._fields = self._process_and_get_fields()

        # Set all instance-level field values to defaults
        if not self._is_loaded:
            for k,v in self._fields.items():
                setattr(self, k, v._default)
                # descriptor = self.__class__.__dict__[k]
                # descriptor.set_original(self, copy.deepcopy(v._default)) # should look at immutability checks

        # Add kwargs to instance
        for k,v in kwargs.items():
            # if isinstance(getattr(self, k), ListField):
            #     print v
            if self._is_loaded:
                if k in self._fields:
                    descriptor = self.__class__.__dict__[k]
                    descriptor.set_original(self, copy.deepcopy(v))
            else:
                setattr(self, k, v)