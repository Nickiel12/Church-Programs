import os
import shelve
import pathlib2

path = pathlib2.Path(os.path.join(os.path.abspath(__file__)))
path = path.parents[0]
path = path/"options"/"data"


shelf = shelve.open(str(path))
shelf.close()