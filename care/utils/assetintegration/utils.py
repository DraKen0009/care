class MutableEnumMember:
    """
    Represents a member of the MutableEnum with name and value.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}, value={self.value}>"

    def __str__(self):
        return self.name


class MutableEnumMeta(type):
    """
    Metaclass to mimic enum behavior with mutability.
    """

    def __iter__(cls):
        return iter(cls._registry.values())

    def __getitem__(cls, name):
        return cls._registry[name]

    def __getattr__(cls, name):
        if name in cls._registry:
            return cls._registry[name]
        error = f"{name} not found in {cls.__name__}"
        raise AttributeError(error)

    def __setattr__(cls, name, value):
        if name.startswith("_"):  # Allow setting private attributes
            super().__setattr__(name, value)
        else:
            cls.register(name, value)


class MutableEnum(metaclass=MutableEnumMeta):
    """
    A base class to mimic enum behavior with mutability.
    """

    _registry = {}

    @classmethod
    def register(cls, name, value):
        """
        Register a new member dynamically.
        """
        if name in cls._registry:
            error = f"{name} is already registered."
            raise ValueError(error)
        cls._registry[name] = MutableEnumMember(name, value)

    @classmethod
    def all(cls):
        """
        Retrieve all registered members.
        """
        return cls._registry.values()

    @classmethod
    def get(cls, name):
        """
        Retrieve a member by name.
        """
        return cls._registry.get(name)
