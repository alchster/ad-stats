class Separator:
    def __init__(self):
        self.added = []
        self.modified = []
        self.removed = []
        self.unchanged = []

    def __repr__(self):
        return "Added: %d\nModified: %d\nUnchanged: %d\nRemoved: %d" % \
            (len(self.added), len(self.modified),
             len(self.unchanged), len(self.removed))
