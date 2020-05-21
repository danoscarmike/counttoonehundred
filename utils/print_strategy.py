class PrintStrategy:
    target = None
    source = None
    counter = None
    plural_format = "service"

    def __init__(self):
        pass

    def parse_kwargs(self, kwargs):
        self.counter = kwargs.get("counter")
        self.source = kwargs.get("source")
        self.target = kwargs.get("target")
        if kwargs.get("noun"):
            self.plural_format = kwargs.get("noun")

        if self.counter and self.counter == 1:
            self.plural_format = "service"
        else:
            self.plural_format = "services"

    def print_update_success(self, **kwargs):
        self.parse_kwargs(kwargs=kwargs)
        print(f"Updated {self.target} with {self.counter} new {self.plural_format}.")

    def print_find_success(self, **kwargs):
        self.parse_kwargs(kwargs=kwargs)
        print(f"Found {self.counter} services in {self.source}.")


if __name__ == "__main__":
    ps = PrintStrategy()
    ps.print_update_success(target="filename", counter=12)
