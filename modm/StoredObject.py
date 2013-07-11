import copy

from SchemaObject import SchemaObject

class StoredObject(SchemaObject):

    _cache = {} # todo implement this with save and load

    def __init__(self, **kwargs):
        self._dirty = []
        self._backrefs = {}
        self._is_loaded = False # this gets passed in via kwargs in self.load
        self._is_optimistic = self._meta.get('optimistic') if hasattr(self, '_meta') else None
        super(StoredObject, self).__init__(**kwargs)

    def resolve_dirty(self):
        while self._dirty:
            i = self._dirty.pop()
            if i[0] == 'backref':
                kwargs = i[1]
                object_with_backref = kwargs['object_with_backref']
                backref_key = kwargs['backref_key']
                backref_value_class_name = self.__class__.__name__.lower()
                backref_value_primary_key = self._primary_key
                object_with_backref._set_backref(backref_key, backref_value_class_name, backref_value_primary_key)

    def _set_backref(self, backref_key, backref_value_class_name, backref_value_primary_key):
        if backref_key not in self._backrefs:
            self._backrefs[backref_key] = {}
        if backref_value_class_name not in self._backrefs[backref_key]:
            self._backrefs[backref_key][backref_value_class_name] = []
        self._backrefs[backref_key][backref_value_class_name].append(backref_value_primary_key)
        self.save()

    @classmethod
    def set_storage(cls, storage):
        if not hasattr(cls, '_storage'):
            cls._storage = []
        cls._storage.append(storage)
        cls.register()

    @classmethod
    def load(cls, key, data=None):
        if not data:
            data = copy.deepcopy(cls._storage[0].get(key)) # better way to do this? Otherwise on load, the Storage.store
                                                       #  look just like changed object
        if not data:
            return None
        data['_is_loaded'] = True
        return cls(**data)

    def _get_original_object(self):
        new_object = self.__class__.load(None, data=self.to_storage(original=True))
        return new_object

    def _get_modified_object(self):
        new_object = self.__class__.load(None, data=self.to_storage())
        return new_object

    def save(self):
        for field_name, field_descriptor in self._fields.items():
            print field_descriptor.do_diff(self)

        if self._is_loaded:
            self._storage[0].update(self._primary_key, self.to_storage())
        elif self._is_optimistic:
            self._primary_key = self._storage[0].optimistic_insert(self.to_storage(), self._primary_name) # do a local update; no dirty
        else:
            self._storage[0].insert(self._primary_key, self.to_storage())

        self._is_loaded = True
        # self.resolve_dirty()

        return True # todo raise exception on not save

    def __getattr__(self, item):
        if item in self._backrefs:
            return self._backrefs[item]
        raise AttributeError(item + ' not found')

    def __getattribute__(self, name):
        return super(StoredObject, self).__getattribute__(name)