from django.contrib import messages
from django.contrib.messages import constants
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio


def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        # PS: Tentar futuramente não carregar todo banco na memoria
        flashcards = Flashcard.objects.filter(user=request.user)
        # Filtragens
        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar)
        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)

        return render(
            request,
            'novo_flashcard.html',
            {
                'categorias': categorias,
                'dificuldades': dificuldades,
                'flashcards': flashcards,
                # para comparar com categoria.id
                'categoria_filtrar': int(categoria_filtrar) if categoria_filtrar != None and
                                                               categoria_filtrar.strip().isdigit() else None,
                'dificuldade_filtrar': dificuldade_filtrar,
            }
        )
    elif request.method == 'POST':
        #cria  o flashcard
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(
                request,
                constants.ERROR,
                'Preencha os campos de pergunta e resposta',
            )
            return redirect('/flashcard/novo_flashcard')

        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,
        )
        flashcard.save()

        messages.add_message(
            request, constants.SUCCESS, 'Flashcard criado com sucesso'
        )
        return redirect('/flashcard/novo_flashcard')


def deletar_flashcard(request, id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    # desafio proposto no video da segunda aula! Proibir exclusão de cards de outros usuarios! - Feito
    try:
        flashcard = Flashcard.objects.get(user=request.user, id=id)
        flashcard.delete()
        messages.add_message(
            request, constants.ERROR, 'Flashcard deletado com sucesso!'
        )
        return redirect('/flashcard/novo_flashcard')

    except Flashcard.DoesNotExist:
        messages.add_message(
            request,
            constants.ERROR,
            'Flashcard não encontrado para o usuario:' + request.user.username,
        )
        return redirect('/flashcard/novo_flashcard')


def iniciar_desafio(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    #EXIBE A TELA DE INICIAR DESAFIOS
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES

        return render(
            request,
            'iniciar_desafio.html',
            {'categorias': categorias, 'dificuldades': dificuldades},
        )
    #CRIA O DESAFIO
    elif request.method == 'POST':

        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade,
        )

        try:
            # Realiza a validação do modelo
            desafio.full_clean()
        except ValidationError as e:
            #para reload da pagina
            categorias2 = Categoria.objects.all()
            dificuldades = Flashcard.DIFICULDADE_CHOICES
            # Se houver erros de validação, retorne o formulário com os erros
            return render(request, 'iniciar_desafio.html', {'desafio': desafio,
                                                            'errors': e.message_dict,
                                                            'categorias': categorias2,
                                                            'dificuldades': dificuldades, })

        #BUSCA OS FLASHCARDS RELACIONADOS
        flashcards = Flashcard.objects.filter(user=request.user).filter(dificuldade=dificuldade).filter(categoria_id__in=categorias).order_by('?')

        #PS: Desafio da Aula 2 - Exibir Messeges
        if flashcards.count() < int(qtd_perguntas):
            messages.add_message(
                request,
                constants.ERROR,
                f'Quantidade de Flashcards para essa combinação insuficiente: {flashcards.count()}',
            )
            return redirect('/flashcard/iniciar_desafio/')

        #SALVA PRIMEIRA ANTES DE ADD AS CATEGORIAS
        desafio.save()
        # ADICIONA TODAS AS CATEGORIAS SELECIONADAS MANY TO MANY
        desafio.categoria.add(*categorias)
        flashcards = flashcards[: int(qtd_perguntas)]

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)
        desafio.save()
        return redirect(f'/flashcard/desafio/{desafio.id}')


def listar_desafio(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    # desenvolver os status (coluna) - Feito

    categoria_filtrar = request.GET.get('categoria')
    dificuldade_filtrar = request.GET.get('dificuldade')
    categorias = Categoria.objects.all()
    dificuldades = Flashcard.DIFICULDADE_CHOICES

    # all
    desafios = Desafio.objects.filter(user=request.user)

    if categoria_filtrar:
        desafios = desafios.filter(categoria__id=categoria_filtrar)
    if dificuldade_filtrar:
        desafios = desafios.filter(dificuldade=dificuldade_filtrar)

    return render(
        request,'listar_desafio.html',
        {
            'categorias': categorias,
            'dificuldades': dificuldades,
            'desafios': desafios,
            'categoria_filtrar': int(categoria_filtrar) if categoria_filtrar != None and
                                                           categoria_filtrar.strip().isdigit() else None,
            'dificuldade_filtrar': dificuldade_filtrar,
        })


def desafio(request, id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    # uma forma de implantar a segurança
    try:
        desafio = Desafio.objects.get(id=id)

        if not desafio.user == request.user:
            raise Http404()
    except (Desafio.DoesNotExist, Http404) as e:
        messages.add_message(
            request,
            constants.ERROR,
            'Desafio não existe para o usuário: ' + request.user.username.upper(),
        )
        return redirect('/flashcard/listar_desafio')

    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()
        return render(
            request,
            'desafio.html',
            {
                'desafio': desafio,
                'acertos': acertos,
                'erros': erros,
                'faltantes': faltantes
            },
        )


def responder_flashcard(request, id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    flashcard_desafio = FlashcardDesafio.objects.get(id=id)

    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()

    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')
    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()
    return redirect(f'/flashcard/desafio/{desafio_id}/')

def relatorio(request, id):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))

    desafio = Desafio.objects.get(id=id)


    acertos = desafio.flashcards.filter(acertou=True).count()
    erros = desafio.flashcards.filter(acertou=False).count()

    #qtde
    dados = [acertos, erros]

    categorias = desafio.categoria.all()
    name_categoria = [i.nome for i in categorias]

    #labels
    dados2 = []

    for categoria in categorias:
        dados2.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count())


    #fazer
    melhores_materias = []
    piores_materias = []


    return render(request, 'relatorio.html', {'desafio': desafio, 'dados': dados, 'categorias': name_categoria, 'dados2': dados2,},)
