import pandas as pd
import datajoint as dj
from itertools import filterfalse

def hdf5(cls):
    """
    Decorator that equips a datajoint class with the ability to save and load it's data from hdf5.
    Internally uses pandas to save and load the data.

    .. code-block:: python
       :linenos:

        import datajoint as dj
        from djaddon import hdf5

        schema = dj.schema('mydb',locals())

        @schema
        @hdf5
        class MyRelation(dj.Computed):
            definition = ...


    """

    def to_hdf5(self, filepath):
        """
        Save the content of this table to the given hdf5 file.

        :param filepath: file path to which the data will be saved
        """
        df = pd.DataFrame(self.fetch())
        df.to_hdf(filepath, cls.__name__)

    def read_hdf5(self, filepath, **kwargs):
        """
        Read contents from hdf5 file into relation. Must haven been saved with `to_hdf5`.

        Keyword arguments are passed on to insert.

        :param filepath: path to the hdf5 file
        """
        df = pd.read_hdf(filepath, cls.__name__)
        self.insert([v.to_dict() for _, v in df.iterrows()], **kwargs)

    cls.to_hdf5 = to_hdf5
    cls.read_hdf5 = read_hdf5

    return cls


def save2hdf5(filename, module):
    """
    Saves all elements from a given module that are subclasses of datajoint.BaseRelation.

    The relations do not need to be decorated with the hdf5 decorator.

    :param filename: filename to save to
    :param module: module containing relations
    """
    for cls in map(lambda c: getattr(module, c), filterfalse(lambda x: x.startswith('__'), dir(module))):
        if issubclass(cls, dj.BaseRelation):
            print('Saving', cls.__name__)
            klass = hdf5(cls)
            klass().to_hdf5(filename)