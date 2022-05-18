# saving and loading data
import os, io
import pickle

show_prints = True

def save(data, filename, overwrite=True):
    if overwrite or not os.path.exists(filename):
        if show_prints:
            print("Saving  -> {}".format(filename))
        with open(filename, "wb") as f:
            pickle.dump(data, f)

def load(filename, default_data=[]):
    data = default_data
    if os.path.exists(filename):
        if show_prints:
            print("Loading <- {}".format(filename))
        with open(filename, "rb") as f:
            data = pickle.load(f)
    return data
