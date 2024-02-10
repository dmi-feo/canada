class ID(str):
    @property
    def path(self):
        return f"#{self}"
