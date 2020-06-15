class InvalidZipCodeError(Exception):
    def __init__(self, message='O CEP informado é inválido.'):
        self.message = message
        super().__init__(self.message)


class ZipCodeOutOfAvailableZone(Exception):
    def __init__(self, message='O CEP informado ainda não é atendido.'):
        self.message = message
        super().__init__(self.message)
