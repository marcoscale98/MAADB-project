class InterfaceException(Exception):
    """
    lanciata quando viene chiamato un metodo di una interfaccia
    """
    def __init__(self):
        super().__init__("This class in an interface")