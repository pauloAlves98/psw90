from django.contrib.auth.models import User
from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=20)
    def __str__(self):
        return self.nome

class Flashcard(models.Model):
    DIFICULDADE_CHOICES = (('D', 'Difícil'), ('M', 'Médio'), ('F', 'Fácil'))
    #um usuario pode ter um ou mais flashcards!
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    pergunta = models.CharField(max_length=100, )
    resposta = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)
    dificuldade = models.CharField(max_length=1, choices=DIFICULDADE_CHOICES)

    @property
    def css_dificuldade(self):
        if self.dificuldade == 'F':
            return 'flashcard-facil'
        elif self.dificuldade == 'M':
            return 'flashcard-medio'
        elif self.dificuldade == 'D':
             return 'flashcard-dificil'

    def __str__(self):
        return self.pergunta

class FlashcardDesafio(models.Model):
    flashcard = models.ForeignKey(Flashcard, on_delete=models.DO_NOTHING)
    respondido = models.BooleanField(default=False)
    acertou = models.BooleanField(default=False)

    def __str__(self):
        return self.flashcard.pergunta
class Desafio(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=100, blank=False, null=False,  error_messages={
             'blank':'Selecione um titulo',
            'null': 'Selecione um título.',
        })
    categoria = models.ManyToManyField(Categoria, blank=False, null=False,  error_messages={
             'blank':'Selecione uma ou mais categorias!',
        'null': 'Selecione uma ou mais categorias.',
        })
    quantidade_perguntas = models.IntegerField(default=1, blank=False, null=False, error_messages={
             'blank':'Adicione uma ou mais perguntas',
             'null': 'Selecione uma ou mais perguntas.',
        })
    dificuldade = models.CharField(
    max_length=1, choices=Flashcard.DIFICULDADE_CHOICES)
    flashcards = models.ManyToManyField(FlashcardDesafio)

    @property
    def status(self):
        if self.flashcards.filter(respondido=False).count()==0:
            return 'CONCLUIDO'
        else:
            return 'INCOMPLETO'
    def __str__(self):
        return self.titulo
