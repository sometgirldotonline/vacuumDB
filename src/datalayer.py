# this "middleware" pickles and unpickles the JSON data.
import inflater
import pickle

def store(data, vdb):
    inflater.store_obf_bloat(vdb, pickle.dumps(data))
def get(vdb):
    return pickle.loads(inflater.retrieve_obf_bloat(vdb))