"""A more or less complete user-defined wrapper around dictionary objects."""

def smallest_diff_key(A, B):
    """return the smallest key adiff in A such that A[adiff] != B[bdiff]"""
    diff_keys = [k for k in A if A.get(k) != B.get(k)]
    return min(diff_keys)

def dict_cmp(A, B):
    if len(A) != len(B):
        return mycmp(len(A), len(B))
    adiff = smallest_diff_key(A, B)
    bdiff = smallest_diff_key(B, A)
    if adiff != bdiff:
        return mycmp(adiff, bdiff)
    return mycmp(A[adiff], B[bdiff])

def mycmp(A, B):
    if isinstance(A, dict) and isinstance(B, dict):
        return dict_cmp(A, B)
    try:
        return A < B
    except TypeError:
        print("Error: on comparison")
        exit(-1)

class DictMixin:
    # Mixin defining all dictionary methods for classes that already have
    # a minimum dictionary interface including getitem, setitem, delitem,
    # and keys. Without knowledge of the subclass constructor, the mixin
    # does not define __init__() or copy().  In addition to the four base
    # methods, progressively more efficiency comes with defining
    # __contains__(), __iter__(), and iteritems().

    # second level definitions support higher levels
    def __iter__(self):
        for k in self.keys():
            yield k
    def has_key(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True
    def __contains__(self, key):
        return self.has_key(key)

    # third level takes advantage of second level definitions
    def iteritems(self):
        for k in self:
            yield (k, self[k])
    def iterkeys(self):
        return self.__iter__()

    # fourth level uses definitions from lower levels
    def itervalues(self):
        for _, v in self.iteritems():
            yield v
    def values(self):
        return [v for _, v in self.iteritems()]
    def items(self):
        return list(self.iteritems())
    def clear(self):
        for key in self.keys():
            del self[key]
    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default
    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError("pop expected at most 2 arguments, got "\
                              + repr(1 + len(args)))
        try:
            value = self[key]
        except KeyError:
            if args:
                return args[0]
            raise
        del self[key]
        return value
    def popitem(self):
        try:
            k, v = next(self.iteritems())
        except StopIteration:
            raise KeyError('container is empty')
        del self[k]
        return (k, v)
    def update(self, other=None, **kwargs):
        # Make progressively weaker assumptions about "other"
        if other is None:
            pass
        elif hasattr(other, 'iteritems'):  # iteritems saves memory and lookups
            for k, v in other.iteritems():
                self[k] = v
        elif hasattr(other, 'keys'):
            for k in other.keys():
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v
        if kwargs:
            self.update(kwargs)
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
    def __repr__(self):
        return repr(dict(self.iteritems()))
    def __cmp__(self, other):
        if other is None:
            return 1
        if isinstance(other, DictMixin):
            other = dict(other.iteritems())
        return dict_cmp(dict(self.iteritems()), other)
    def __len__(self):
        return len(self.keys())
