class Separator:
    added = []
    modified = []
    removed = []
    unchanged = []

    def __repr__(self):
        return "Added: %d\nModified: %d\nUnchanged: %d\nRemoved: %d" % \
            (len(self.added), len(self.modified),
             len(self.unchanged), len(self.removed))
