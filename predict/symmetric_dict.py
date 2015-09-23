class SymmetricDict(dict):
    def __getitem__(self, key):
        return dict.__getitem__(self,
                                key if key[0] < key[1] else (key[1], key[0]))

    def __setitem__(self, key, value):
        dict.__setitem__(self, key if key[0] < key[1] else (key[1],key[0]),
                         value)
