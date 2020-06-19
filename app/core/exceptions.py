class InvalidZipCodeError(Exception):
    def __init__(self, message='O CEP informado é inválido.'):
        self.message = message
        super().__init__(self.message)


class InvalidSenderError(Exception):
    def __init__(self, message='O usuário informado não é um Cliente.'):
        self.message = message
        super().__init__(self.message)


class InvalidEmailError(Exception):
    def __init__(self, message='O e-mail informado não é válido.'):
        self.message = message
        super().__init__(self.message)


class ZipCodeOutOfAvailableZone(Exception):
    def __init__(self, message='O CEP informado ainda não é atendido.'):
        self.message = message
        super().__init__(self.message)


class InvitationLimitExceeded(Exception):
    def __init__(self, message='O usuário não tem convites disponíveis.'):
        self.message = message
        super().__init__(self.message)
