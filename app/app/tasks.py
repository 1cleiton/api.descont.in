from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def send_invite(sender, to):
    print(f'Olá, você foi convidado pelo {sender} a juntar-se a ele na plataforma\
        Descontin para aproveitar os melhores descontos do seu bairro.')
