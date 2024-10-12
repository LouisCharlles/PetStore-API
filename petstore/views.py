from django.views import View
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario,Pet,Veterinario,Consulta
from django.core import serializers
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from datetime import datetime
import pytz
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie,vary_on_headers
from decouple import config
from django.contrib.auth.hashers import make_password
import re
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from drf_yasg import openapi
def validar_senha(senha):
    """
    Valida a senha fornecida de acordo com os seguintes critérios:
    - Deve ter pelo menos 7 caracteres e no máximo 200.
    - Deve conter pelo menos um caractere especial, uma letra maiúscula e uma letra minúscula.

    Args:
        senha (str): A senha a ser validada.

    Returns:
        str: Mensagem de erro se a senha não for válida, caso contrário, retorna None.
    """
    especiais = '!@#$%&*-+()<>|\=-'
    minusculas = 'ABCDEFGHIKLMNOPQRSTUVWXYZÇ'.lower()
    maiusculas = 'ABCDEFGHIKLMNOPQRSTUVWXYZÇ'

    flag_especial = any(caracter in especiais for caracter in senha)
    flag_maiuscula = any(caracter in maiusculas for caracter in senha)
    flag_minuscula = any(caracter in minusculas for caracter in senha)

    if len(senha) <= 6:
        return "Sua senha deve conter no mínimo 7 caracteres."
    elif len(senha) > 200:
        return "Sua senha deve conter no máximo 200 caracteres."

    if not flag_especial or not flag_maiuscula or not flag_minuscula:
        return "Sua senha deve conter caracteres especiais, maiúsculas e minúsculas."

    return None

       
def validar_email(email:str):
    """
    Valida o formato de um endereço de e-mail de acordo com regras específicas:
    - Não pode conter caracteres especiais não permitidos.
    - Não pode conter espaços ou dois pontos consecutivos.
    - O domínio deve conter pelo menos um ponto.
    - O comprimento máximo é de 64 caracteres.
    - A parte local antes do "@" deve ter pelo menos 3 caracteres.

    Args:
        email (str): O endereço de e-mail a ser validado.

    Returns:
        str: Mensagem de erro se o e-mail não for válido, caso contrário, retorna None.
    """
    caracteres_na0_permitidos = set("&='-+,<>~!$%^*}{?¨|/'\\][;")

    if any(caractere in caracteres_na0_permitidos for caractere in email):
        return f"Caractere nao permitido na composicao do email."
    
    elif ".." in email:
        return "Um email nao pode ter dois pontos consecutivos em sua composicao."
    
    elif " " in email:
        return "Espacos vazios nao sao permitidos na composicao do email."
    
    elif "@" not in email:
        return "@ é obrigatorio no email."
    
    local,_,dominio = email.partition("@")
    if len(local)<3:
        return "O numero de caracteres deve ser no minimo que 3 antes do @."
     
    if len(email)>64:
        return "O email deve ter no maximo 64 caracteres."
    
    if "." not in dominio:
        return "Domínio inválido na composicao do email. Ele deve conter pelo menos 1 ponto."
    
    regex_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z-.]{3,}$'
    if not re.match(regex_email,email):
        return "Padrão de email incorreto."
    
    return None

@method_decorator(csrf_exempt, name="dispatch")
class CreateUsuarioView(APIView):
    """
    View responsável por criar um novo usuário na aplicação.
    
    Métodos:
        post(request): Cria um novo usuário baseado nos dados fornecidos no corpo da requisição.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nome': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do usuário'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='E-mail do usuário'),
                'senha': openapi.Schema(type=openapi.TYPE_STRING, description='Senha do usuário'),
            },
            required=['nome', 'email', 'senha']
        ),
        responses={
            201: openapi.Response('ID do novo usuário', openapi.Schema(type=openapi.TYPE_INTEGER)),
            400: 'Erro ao criar usuário'
        }
    )
    def post(self, request):
        """
        Cria um novo usuário na base de dados após validar o e-mail e a senha fornecidos.
        
        Args:
            request (HttpRequest): Objeto da requisição contendo os dados do novo usuário (nome, email e senha).

        Returns:
            JsonResponse: ID do novo usuário se criado com sucesso ou mensagem de erro em caso de falha.
        """

        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            email = data.get('email')
            senha = data.get('senha')

            usuario = Usuario.objects.filter(email__iexact=email)

            email_error = validar_email(email=email)
            senha_error = validar_senha(senha=senha)
            
            if email_error:
                return JsonResponse({"ERROR": f"{email_error}"},status=400)
            elif senha_error:
                return JsonResponse({"ERROR": f"{senha_error}"}, status=400)
                 
            elif usuario.exists():
                return JsonResponse({'error': 'Usuário já existe.'}, status=400)

            hashed_senha = make_password(senha)

            usuario = Usuario.objects.create(nome=nome, email=email, senha=hashed_senha)
            
            return JsonResponse({'id': usuario.id_usuario}, status=201)
        except TypeError as error:
            return JsonResponse({
                "Error": "Tentativa de cadastro com credenciais inválidas. Verifique o campo de email e senha e insira valores válidos, caracteres númericos e alfabéticos por exemplo."
            }, status=400)
        
class GetUsuarioInfoView(APIView):
    """
    View para buscar as informações de um usuário pelo seu ID.
    
    Métodos:
        get(*args, **kwargs): Retorna os detalhes do usuário baseado no ID fornecido.
    """
    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'id_usuario',
            openapi.IN_PATH,
            description="ID do usuário a ser buscado",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200:openapi.Response('Detalhes do usuário',openapi.Schema(type=openapi.TYPE_OBJECT,properties={
            'id_usuario':openapi.Schema(type=openapi.TYPE_INTEGER),
            'nome':openapi.Schema(type=openapi.TYPE_STRING),
            'email':openapi.Schema(type=openapi.TYPE_STRING),
            "senha":openapi.Schema(type=openapi.TYPE_STRING),
        })),
        404:'Nenhum usuário com este id foi encontrado.',
        400: 'Erro na requisição.'
    })
    def get(self, *args, **kwargs):
        """
        Retorna os detalhes de um usuário específico com base no ID.
        
        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos de palavra-chave contendo o ID do usuário.
        
        Returns:
            JsonResponse: Informações do usuário se encontrado ou mensagem de erro caso contrário.
        """

        id_usuario = kwargs.get('id_usuario')
        try:
            usuario = Usuario.objects.filter(id_usuario=id_usuario).values('id_usuario', 'nome', 'email', 'senha').first()
            if usuario:
                return JsonResponse(usuario, status=200)  # safe=True is the default
            else:
                return JsonResponse({'status': 'erro', 'mensagem': 'Nenhum usuário com este id foi encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({f"Error":{e}},status=400)

        
@method_decorator(csrf_exempt,name="dispatch")
class UpdateUsuarioView(APIView):
    """
    View responsável por atualizar as informações de um usuário existente.
    
    Métodos:
        put(request, *args, **kwargs): Atualiza os dados do usuário com base no ID fornecido.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'nome': openapi.Schema(type=openapi.TYPE_STRING, description="Nome do usuário"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="E-mail do usuário"),
            'senha': openapi.Schema(type=openapi.TYPE_STRING, description="Senha do usuário"),
        },
        required=['nome', 'email', 'senha']
    ),
    responses={
        200: openapi.Response(
            description='Detalhes do usuário atualizado',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id_usuario': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'nome': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        404: openapi.Response(
            description="Nenhum usuário com este ID foi encontrado.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        ),
        400: openapi.Response(
            description="Erro ao tentar atualizar o usuário.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        )
    }
)
    def put(self,request,*args, **kwargs):
        """
        Atualiza as informações de um usuário (nome, e-mail e senha) com base no ID.

        Args:
            request (HttpRequest): Objeto da requisição contendo os novos dados.
            *args: Argumentos posicionais.
            **kwargs: Argumentos de palavra-chave contendo o ID do usuário.

        Returns:
            JsonResponse: Informações do usuário atualizado ou mensagens de erro em caso de falha.
        """

        id_usuario = kwargs.get('id_usuario')
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            email = data.get('email')
            senha = data.get('senha')

            email_error = validar_email(email=email)
            senha_error = validar_senha(senha=senha)
            if email_error:
                return JsonResponse({"ERROR": f"{email_error}"},status=400)
            elif senha_error:
                return JsonResponse({"ERROR":f"{senha_error}"},status=400)
            elif not isinstance(senha,str):
                return JsonResponse({'error':"A senha deve ser em caracteres não contendo apenas números."},status=400)
            elif not isinstance(email, str) or not isinstance(senha, str):
                return JsonResponse({'error': 'Email e senha devem ser strings.'}, status=400)
            
            elif not Usuario.objects.filter(id_usuario=id_usuario).exists():
                return JsonResponse({'error': 'Usuário não existe.'}, status=404)
            
             
            hashed_senha = make_password(senha)

            usuario = Usuario.objects.filter(id_usuario=id_usuario).update(nome=nome,email=email,senha=hashed_senha)

            if not usuario:
                return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum usuário com este id foi encontrado.'}, status=404)
            
            usuario_atualizado = Usuario.objects.filter(id_usuario=id_usuario).values('id_usuario','nome','email','senha').first()
            return JsonResponse(usuario_atualizado,status=200,safe=False)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)
        except TypeError as error:
            return JsonResponse({"Error: tentativa de cadastro com credenciais diferentes de caracteres alfabéticos, use letras e simbolos na sua senha se estiver tentando cadastrar apenas com números.":error},status=400)

@method_decorator(csrf_exempt,'dispatch')
class DeleteUsuarioView(APIView):
    """
    View responsável por deletar um usuário da base de dados.
    
    Métodos:
        delete(*args, **kwargs): Deleta o usuário com base no ID fornecido.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    def delete(self,*args, **kwargs):
        """
        Deleta um usuário da base de dados com base no ID fornecido.

        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos de palavra-chave contendo o ID do usuário.

        Returns:
            JsonResponse: Confirmação de deleção ou mensagem de erro em caso de falha.
        """
        id_usuario = kwargs.get('id_usuario')
        try:
            usuario = Usuario.objects.get(id_usuario=id_usuario)
            usuario.delete()
            return JsonResponse("Usuário deletado com sucesso.",status=200,safe=False)
        except Usuario.DoesNotExist:
            return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum usuário com este id foi encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)

@method_decorator(csrf_exempt,'dispatch')
class UsuarioMarcaConsultaView(APIView):
    """
    View para marcar uma consulta entre um veterinário e um pet para um usuário específico.
    
    Métodos:
        post(request, *args, **kwargs): Marca a consulta com base no ID do usuário.
    """
    @method_decorator(cache_page(60*60*2))
    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={
        'veterinario': openapi.Schema(type=openapi.TYPE_INTEGER,description="id do veterinário"),
        'pet':openapi.Schema(type=openapi.TYPE_INTEGER,description="id do pet pertencente ao dono")
    },
    required=['veterinario','pet']
    ),
    responses={
        201:openapi.Response("ID da consulta gerada",openapi.Schema(type=openapi.TYPE_INTEGER)),
        404: "Nenhum Veterinário ou pet foram encontrados com o(s) id provido.",
        400:"Ocorreu um erro ao fazer a requisição."
    })
    def post(self,request,*args,**kwargs):
        """
        Marca uma nova consulta entre um veterinário e um pet para o usuário especificado.

        Args:
            request (HttpRequest): Objeto da requisição contendo os IDs do pet e do veterinário.
            *args: Argumentos posicionais.
            **kwargs: Argumentos de palavra-chave contendo o ID do usuário.

        Returns:
            JsonResponse: Detalhes da consulta criada ou mensagem de erro em caso de falha.
        """
        id_usuario = kwargs.get('id_usuario')
        try:
            usuario = Usuario.objects.filter(id_usuario=id_usuario)
        
            if not usuario:
                return JsonResponse(f"Usuário não encontrado.",status=404,safe=False)
            
            body = json.loads(request.body.decode('utf-8'))

            pet = Pet.objects.get(id_pet=body['pet'])
            vet = Veterinario.objects.get(id_veterinario=body['veterinario'])

            consulta = Consulta.objects.create(veterinario=vet,pet=pet)
            data = json.loads(serializers.serialize('json',[consulta]))
            return JsonResponse(data=data,status=201,safe=False)    
        except Pet.DoesNotExist:
            return JsonResponse(f"Este pet não pôde ser encontrado.",status=404,safe=False)
        except Veterinario.DoesNotExist:
            return JsonResponse(f"O veterinário não pôde ser encontrado.",status=404,safe=False)
        except Exception as e:
            return JsonResponse(f"Ocorreu um erro: {e}",status=400,safe=False)
        
class UsuarioVizualizaConsultaView(APIView):
    """
    View para visualizar os detalhes de uma consulta marcada.
    
    Métodos:
        get(*args, **kwargs): Retorna os detalhes da consulta com base no ID.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self,*args,**kwargs):
        """
        Retorna os detalhes de uma consulta marcada com base no ID fornecido.

        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos de palavra-chave contendo o ID da consulta.

        Returns:
            JsonResponse: Detalhes da consulta ou mensagem de erro em caso de falha.
        """
        id_consulta = kwargs.get('id_consulta')
        try:
            consulta = Consulta.objects.filter(id_consulta=id_consulta).select_related('veterinario','pet').values('id_consulta','data_consulta','realizada','veterinario__nome','pet__nome').first()
            if not consulta:
                return JsonResponse("Não foi possível encontrar a consulta com esse identificador.",status=404,safe=False)
            
            return JsonResponse(consulta,status=200,safe=False)
        except Exception as e:
            return JsonResponse(f"Uma exceção foi lançada: {e}",status=400,safe=False)

@method_decorator(csrf_exempt,name="dispatch")
class CreatePetVIew(APIView):
    """
    View responsável por criar um novo pet.

    Métodos:
    - post(request): Cria um novo pet a partir dos dados fornecidos no corpo da requisição.

    Exceções:
    - Retorna erro 400 caso os dados fornecidos estejam incorretos (nome, espécie, idade ou dono do pet).
    - Retorna erro 404 caso o dono do pet não seja encontrado no banco de dados.
    - Retorna erro 400 em caso de exceções de tipo.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={
        'nome':openapi.Schema(type=openapi.TYPE_STRING,description="Nome do pet"),
        'especie':openapi.Schema(type=openapi.TYPE_STRING,description="Especie do pet"),
        'idade':openapi.Schema(type=openapi.TYPE_INTEGER,description="Idade do pet"),
        'dono_do_pet':openapi.Schema(type=openapi.TYPE_INTEGER,description="id do dono do pet")
    },
    required=['nome','especie','idade','dono_do_pet']
    ),
    responses={
        201: openapi.Response('ID do novo pet', openapi.Schema(type=openapi.TYPE_INTEGER)),
        404:"Não foi possível encontrar um usuário com esse id.",
        400:"Ocorreu um erro ao cadastrar o pet."
    }
    )
    def post(self,request):
        """
        Cria um pet e o associa a um dono. Valida os dados recebidos antes de salvar no banco.

        Parâmetros:
        - request (HttpRequest): Requisição HTTP contendo os dados do pet no corpo.

        Retornos:
        - JsonResponse: Contém o pet criado em formato JSON ou mensagem de erro.
        """
        try:
            body = json.loads(request.body)

            nome = body['nome']
            especie = body['especie']
            idade = body['idade']
            dono = body['dono_do_pet']

            if not isinstance(nome,str) or not isinstance(especie,str):
                return JsonResponse({'erro: o nome e especie precisam ser inseridos corretamente.'},status=400,safe=False)
            if not isinstance(idade,int):
                return JsonResponse({"erro: idade precisa ser um número inteiro."},status=400,safe=False)
            if not Usuario.objects.filter(id_usuario=dono).exists():
                return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum usuário com este id foi encontrado.'}, status=404,safe=False)
            elif idade<0:
                return JsonResponse({"ERROR":"O campo idade não pode ser preenchido com inteiros negativos."},status=400)
            dono_do_pet = Usuario.objects.get(id_usuario=dono)
            novo_pet = Pet.objects.create(nome=body['nome'],especie=body['especie'],idade=body['idade'],dono_do_pet=dono_do_pet)
            data = json.loads(serializers.serialize('json',[novo_pet]))
            return JsonResponse(data=data,status=201,safe=False)
        except TypeError as e:
           return JsonResponse(f'Insira valores válidos nos campos de nome, especie, idade e dono do pet.',status=400,safe=False)
    

class GetPetInfoView(APIView):
    """
    View responsável por obter informações de um pet com base no seu ID.

    Métodos:
    - get(*args, **kwargs): Retorna os dados do pet a partir do ID fornecido.

    Exceções:
    - Retorna erro 404 caso o pet não seja encontrado.
    - Retorna erro 400 em caso de exceções gerais.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self,*args, **kwargs):
        """
        Busca informações do pet por ID.

        Parâmetros:
        - *args, **kwargs: Argumentos e parâmetros da requisição, incluindo o id_pet.

        Retornos:
        - JsonResponse: Dados do pet ou mensagem de erro.
        """
        id_pet = kwargs.get('id_pet')
        try:
            pet = Pet.objects.filter(id_pet=id_pet).values('id_pet','nome','especie','idade','dono_do_pet').first()
            if not pet:
                return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum pet com este id foi encontrado.'}, status=404)
            
            return JsonResponse(pet,status=200,safe=False)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)
        
@method_decorator(csrf_exempt,'dispatch')
class UpdatePetInfoView(APIView):
    """
    View responsável por atualizar as informações de um pet existente.

    Métodos:
    - put(request, *args, **kwargs): Atualiza o pet com base nos dados fornecidos na requisição.

    Exceções:
    - Retorna erro 400 em caso de dados inválidos (nome, espécie, idade ou dono).
    - Retorna erro 404 caso o pet ou dono não sejam encontrados.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={
        'nome':openapi.Schema(type=openapi.TYPE_STRING,description="Nome do pet"),
        'especie':openapi.Schema(type=openapi.TYPE_STRING,description="Especie do pet"),
        'idade':openapi.Schema(type=openapi.TYPE_INTEGER,description="Idade do pet"),
        'dono_do_pet':openapi.Schema(type=openapi.TYPE_INTEGER,description="id do dono do pet")
    },
    required=['nome','especie','idade','dono_do_pet']
    ),
    responses={
        200: openapi.Response(
            description='Detalhes do pet atualizado',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'nome': openapi.Schema(type=openapi.TYPE_STRING),
                    'especie': openapi.Schema(type=openapi.TYPE_STRING),
                    'idade': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'dono_do_pet': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        404: openapi.Response(
            description="Nenhum usuário dono do pet foi encontrado.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        ),
        400: openapi.Response(
            description="Erro ao tentar atualizar o pet, verifique os campos se estão preenchidos corretamente.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        )
    })
    def put(self,request,*args,**kwargs):
        """
        Atualiza as informações de um pet com base no id_pet e nos dados fornecidos no corpo da requisição.

        Args:
            request: A requisição HTTP que contém o corpo com os dados do pet.
            *args: Argumentos posicionais.
            **kwargs: Argumentos de palavra-chave, incluindo 'id_pet'.

        Returns:
            JsonResponse: O pet atualizado ou uma mensagem de erro.
        """
        id_pet = kwargs.get('id_pet')
        try:
            request_body = json.loads(request.body)
            nome = request_body['nome']
            especie = request_body['especie']
            idade = request_body['idade']
            dono = request_body['dono_do_pet']

            
            if idade<0:
                return JsonResponse({"ERROR":"O campo idade não pode ser preenchido com inteiros negativos."},status=400)
            
            elif not Usuario.objects.filter(id_usuario=dono).exists():
                    return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum usuário com este id foi encontrado.'}, status=404)
           
            pet = Pet.objects.filter(id_pet=id_pet).update(
                nome=nome, 
                especie=especie, 
                idade=idade, 
                dono_do_pet=dono
            )

            if not pet:
                return JsonResponse("O pet não foi encontrado.", status=404, safe=False)

            pet_atualizado = Pet.objects.filter(id_pet=id_pet).values('nome', 'especie', 'idade', 'dono_do_pet').first()
            return JsonResponse(pet_atualizado, status=200, safe=False)
        
        except Exception as e:
            return JsonResponse(f"O seguinte erro aconteceu: {str(e)}",status=400,safe=False)
        
@method_decorator(csrf_exempt,'dispatch')
class DeletePetView(APIView):
    """
    View responsável por deletar um pet existente.

    Métodos:
    - delete(*args, **kwargs): Remove um pet com base no ID fornecido.

    Exceções:
    - Retorna erro 404 caso o pet não seja encontrado.
    - Retorna erro 400 em caso de exceções gerais.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    def delete(self,*args, **kwargs):
        """
        Deleta um pet com base no id_pet fornecido na URL.

        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos de palavra-chave, incluindo 'id_pet'.

        Returns:
            JsonResponse: Uma mensagem de sucesso ou erro.
        """
        id_pet = kwargs.get('id_pet')
        try:
            pet = Pet.objects.filter(id_pet=id_pet)
            if not pet.exists():
                return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum pet com este id foi encontrado.'}, status=404)
            else:
                Pet.objects.filter(id_pet=id_pet).delete()
                return JsonResponse("Pet deletado com sucesso.",status=200,safe=False)
        except Pet.DoesNotExist:
            return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum pet com este id foi encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)
        

@method_decorator(csrf_exempt,name='dispatch')
class CreateVetView(APIView):
    """
    View responsável por criar um novo veterinário.

    Métodos:
    - post(request, *args, **kwargs): Cria um novo veterinário a partir dos dados fornecidos.

    Exceções:
    - Retorna erro 400 em caso de dados inválidos ou caso o veterinário já exista.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nome': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do veterinário'),
                'especialidade': openapi.Schema(type=openapi.TYPE_STRING, description='especialidade do profissional'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='E-mail do veterinário'),
                'senha': openapi.Schema(type=openapi.TYPE_STRING, description='Senha do veterinário'),
            },
            required=['nome','especialidade','email', 'senha']
        ),
        responses={
            201: openapi.Response('ID do novo veterinário gerado:', openapi.Schema(type=openapi.TYPE_INTEGER)),
            400: 'Erro ao criar veterinário'
        }
    )
    def post(self,request,*args,**kwargs):
        """
        Cria um novo veterinário com base nos dados recebidos.

        Parâmetros:
        - request (HttpRequest): Requisição HTTP contendo os dados do veterinário no corpo.

        Retornos:
        - JsonResponse: Dados do veterinário criado ou mensagem de erro.
        """
        try:
            request_body = json.loads(request.body)
            nome = request_body['nome']
            especialidade = request_body['especialidade']
            email = request_body['email']
            senha = request_body['senha']
        
            vet = Veterinario.objects.filter(email__iexact=email)

            try:
                email_error = validar_email(email=email)
                senha_error = validar_senha(senha=senha)
                if senha_error:
                    return JsonResponse({"ERROR":f"{senha_error}"},status=400,safe=False)
                elif email_error:
                    return JsonResponse({"ERROR":f"{senha_error}"},status=400,safe=False)
            except TypeError as e:
                return JsonResponse({"error":f"Só serão aceitos caracteres especiais, maiúsculos e minúsculos na criação da senha."},status=400)
            
            if not isinstance(senha,str):
                return JsonResponse({'error':"A senha deve ser em caracteres não contendo apenas números."},status=400,safe=False)
            
            if not isinstance(nome,str) or not isinstance(especialidade,str) or not isinstance(email,str) or not isinstance(senha,str):
                return JsonResponse("É necessário que os campos nome, especialidade, email e senha estejam preenchidos corretamente.",status=400,safe=False)
            
            if vet.exists():
                return JsonResponse("Este veterinário já existe.",status=400,safe=False)
            
            hashed_senha = make_password(senha)
            new_vet = Veterinario.objects.create(nome=request_body['nome'],especialidade=request_body['especialidade'],email=email,senha=hashed_senha)
            data = json.loads(serializers.serialize('json',[new_vet]))
            return JsonResponse(data=data,status=201,safe=False)
        except TypeError as error:
            return JsonResponse({"Error: tentativa de cadastro com credenciais diferentes de caracteres alfabéticos, use letras e simbolos na sua senha se estiver tentando cadastrar apenas com números.":error},status=400)
        except Exception as e:
            return JsonResponse(f"Exceção lançada: {e}",status=400,safe=False)

class GetVetInfoView(APIView):
    """
    View responsável por obter informações de um veterinário pelo ID.

    Métodos:
    - get(*args, **kwargs): Retorna os dados do veterinário com base no ID fornecido.

    Exceções:
    - Retorna erro 404 caso o veterinário não seja encontrado.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    def get(self,*args,**kwargs):
        """
        Busca informações de um veterinário por ID.

        Parâmetros:
        - *args, **kwargs: Argumentos da requisição, incluindo o id_veterinario.

        Retornos:
        - JsonResponse: Dados do veterinário ou mensagem de erro.
        """
       
        id_veterinario = kwargs.get('id_veterinario')
        try:
            vet = Veterinario.objects.filter(id_veterinario=id_veterinario).values('id_veterinario','nome','especialidade','email','senha').first()
            if not vet:
                return JsonResponse("Nenhum médico veterinário com este id foi encontrado.",status=404,safe=False)
            return JsonResponse(vet,status=200,safe=False)
        except Exception as e:
            return JsonResponse(f"Exceção lançada: {e}",status=400,safe=False)
        
@method_decorator(csrf_exempt,'dispatch')
class UpdateVetInfoView(APIView):
    """
    View responsável por atualizar as informações de um veterinário existente.

    Métodos:
    - put(request, *args, **kwargs): Atualiza os dados de um veterinário a partir das informações fornecidas.

    Exceções:
    - Retorna erro 404 caso o veterinário não seja encontrado.
    - Retorna erro 400 em caso de dados inválidos.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'nome': openapi.Schema(type=openapi.TYPE_STRING, description="Nome do usuário"),
            'especialidade':openapi.Schema(type=openapi.TYPE_STRING, description="Nome do usuário"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="E-mail do usuário"),
            'senha': openapi.Schema(type=openapi.TYPE_STRING, description="Senha do usuário"),
        },
        required=['nome','especialidade','email', 'senha']
    ),
    responses={
        200: openapi.Response(
            description='Detalhes do veterinário foram atualizados.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id_veterinario': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'nome': openapi.Schema(type=openapi.TYPE_STRING),
                    'especialidade': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                    'senha': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        404: openapi.Response(
            description="Nenhum veterinário com este ID foi encontrado.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        ),
        400: openapi.Response(
            description="Erro ao tentar atualizar o veterinário.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        )
    }
)
    def put(self,request,*args,**kwargs):
        """
        Atualiza as informações de um veterinário com base nos dados recebidos.

        Parâmetros:
        - request (HttpRequest): Requisição HTTP contendo os dados do veterinário.
        - *args, **kwargs: Argumentos da requisição, incluindo o id_veterinario.

        Retornos:
        - JsonResponse: Dados atualizados do veterinário ou mensagem de erro.
        """
        id_veterinario = kwargs.get('id_veterinario')
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            especialidade = data.get('especialidade')
            email = data.get('email')
            senha = data.get('senha')

            vet = Veterinario.objects.filter(id_veterinario=id_veterinario)

            email_error = validar_email(email=email)
            senha_error = validar_senha(senha=senha)
            if email_error:
                return JsonResponse({"ERROR":f"{senha_error}"},status=400)
            if senha_error:
                return JsonResponse({"ERROR":f"{senha_error}"},status=400)

            if not isinstance(senha,str):
                return JsonResponse({'error':"A senha deve ser em caracteres não contendo apenas números."},status=400)
            if not vet.exists():
                return JsonResponse("Nenhum médico veterinário com este id foi encontrado.",status=404,safe=False)
            
            hashed_senha = make_password(senha)
            Veterinario.objects.filter(id_veterinario=id_veterinario).update(nome=nome,especialidade=especialidade,email=email,senha=hashed_senha)
            veterinario_atualizado = Veterinario.objects.filter(id_veterinario=id_veterinario).values('id_veterinario','nome','especialidade','email','senha').first()
            return JsonResponse(veterinario_atualizado,status=200,safe=False)
        
        except Exception as e:
            return JsonResponse(f"Exceção lançada: {e}",status=400,safe=False)
        except TypeError as error:
            return JsonResponse({"Error: tentativa de cadastro com credenciais diferentes de caracteres alfabéticos, use letras e simbolos na sua senha se estiver tentando cadastrar apenas com números.":error},status=400)

@method_decorator(csrf_exempt,'dispatch')
class DeleteVetInfoView(APIView):
    """
    View responsável por deletar um veterinário.

    Métodos:
    - delete(*args, **kwargs): Remove um veterinário com base no ID fornecido.

    Exceções:
    - Retorna erro 404 caso o veterinário não seja encontrado.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    def delete(self,*args, **kwargs):
        """
        Remove um veterinário do banco de dados.

        Parâmetros:
        - *args, **kwargs: Argumentos da requisição, incluindo o id_veterinario.

        Retornos:
        - JsonResponse: Confirmação de deleção ou mensagem de erro.
        """
        id_veterinario = kwargs.get('id_veterinario')
        try:
            vet = Veterinario.objects.filter(id_veterinario=id_veterinario)
            if not vet.exists():
                return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum veterinário com este id foi encontrado.'}, status=404)
            else:
                Veterinario.objects.filter(id_veterinario=id_veterinario).delete()
                return JsonResponse("Veterinário deletado com sucesso.",status=200,safe=False)
        except Veterinario.DoesNotExist:
            return JsonResponse({'status': 'erro', 'mensagem': f'Nenhum veterinário com este id foi encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)

@method_decorator(csrf_exempt,'dispatch')
class DefineDataConsultaView(APIView):
    """
    View responsável por definir a data de uma consulta.

    Métodos:
    - put(request, *args, **kwargs): Atualiza a data de uma consulta com base nos dados fornecidos.

    Exceções:
    - Retorna erro 404 caso a consulta não seja encontrada.
    - Retorna erro 400 em caso de dados inválidos.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={
        'data_consulta':openapi.Schema(type=openapi.TYPE_STRING,description="Data da consulta a ser definida.")
    },
    required=['data_consulta']
    ),
    responses={
        200:  openapi.Response(
            description='Detalhes da data da consulta foram atualizados.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data_consulta': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        404: openapi.Response(
            description="Nenhuma consulta com esse id foi encontrada.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        ),
        400: openapi.Response(
            description="Erro ao tentar atualizar os dados da consulta, verifique os campos se estão preenchidos corretamente.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        )
    }
)
    def put(self,request,*args,**kwargs):
        """
        Define a data de uma consulta e marca como realizada se a data for anterior à atual.

        Parâmetros:
        - request (HttpRequest): Requisição HTTP contendo os dados da data da consulta.
        - *args, **kwargs: Argumentos da requisição, incluindo o id_consulta.

        Retornos:
        - JsonResponse: Confirmação de atualização ou mensagem de erro.
        """
       
        id_consulta = kwargs.get('id_consulta')
        try:
            body = json.loads(request.body)
            data_consulta = body['data_consulta']
            consulta = Consulta.objects.get(id_consulta=id_consulta)

            if not consulta:
                return JsonResponse("Essa consulta não existe.",status=404)
            else:
                Consulta.objects.filter(id_consulta=id_consulta).update(data_consulta=data_consulta)
                consulta_atualizada = Consulta.objects.filter(id_consulta=id_consulta).values('data_consulta','realizada').first()

                data_consulta_atualizada = consulta_atualizada['data_consulta']

                timezone = pytz.timezone('America/Fortaleza')
                data_consulta_aware = data_consulta_atualizada.astimezone(timezone)
                now_aware = datetime.now().astimezone(timezone)

                if data_consulta_aware < now_aware:
                    consulta_atualizada['realizada'] = True
                    return JsonResponse(consulta_atualizada,status=200,safe=False)
                else:
                    consulta_atualizada['realizada'] = False
                    return JsonResponse(consulta_atualizada,status=200,safe=False)
        except TypeError:
            return JsonResponse("Será aceito apenas datas: Ano, mês, dia, com horas e minutos.",status=400,safe=False)
        except Consulta.DoesNotExist:
            return JsonResponse("Essa consulta não existe.",status=404,safe=False)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400,safe=False)
        

@method_decorator(csrf_exempt,'dispatch')
class DefineConsultaComoRealizadaView(APIView):
    """
    View responsável por definir uma consulta como realizada.

    Métodos:
    - put(request, *args, **kwargs): Marca a consulta como realizada com base na data.

    Exceções:
    - Retorna erro 404 caso a consulta não seja encontrada.
    - Retorna erro 400 em caso de dados inválidos ou exceções.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,properties={
        'realizada':openapi.Schema(type=openapi.TYPE_STRING,description="Consulta a ser definida como realizada.")
    },
    required=['realizada']
    ),
    responses={
        200:  openapi.Response(
            description='Detalhes da data da consulta foram atualizados.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'data_consulta': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        404: openapi.Response(
            description="Nenhuma consulta com esse id foi encontrada.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        ),
        400: openapi.Response(
            description="Erro ao tentar atualizar os dados da consulta, verifique os campos se estão preenchidos corretamente.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro")
                }
            )
        )
    }
)
    def put(self,request,*args,**kwargs):
        """
        Atualiza o status da consulta para realizada.

        Parâmetros:
        - request (HttpRequest): Requisição HTTP contendo os dados da consulta.
        - *args, **kwargs: Argumentos da requisição, incluindo o id_consulta.

        Retornos:
        - JsonResponse: Confirmação de atualização ou mensagem de erro.
        """
        id_consulta = kwargs.get('id_consulta')
        try:
            body = json.loads(request.body)
            consulta = Consulta.objects.filter(id_consulta=id_consulta)
            realizada = body['realizada']
            
            if not consulta.exists():
                return JsonResponse("Essa consulta não existe.",status=404,safe=False)
            else:
                consulta.update(realizada=realizada)
                consulta_realizada = consulta.values('data_consulta','realizada').first()
                return JsonResponse(consulta_realizada,status=200,safe=False)
        except TypeError:
            return JsonResponse("Esse tipo não é aceito no campo: realizada.",status=400)
        except Consulta.DoesNotExist:
            return JsonResponse("Essa consulta não existe.",status=404,safe=False)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400,safe=False)
            

@method_decorator(csrf_exempt,'dispatch')
class DeleteConsultaView(APIView):
    """
    View responsável por deletar uma consulta.

    Métodos:
    - delete(*args, **kwargs): Remove uma consulta com base no ID fornecido.

    Exceções:
    - Retorna erro 404 caso a consulta não seja encontrada.
    """
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_headers("Authorization"))
    def delete(self,*args,**kwargs):
        """
        Remove uma consulta do banco de dados.

        Parâmetros:
        - *args, **kwargs: Argumentos da requisição, incluindo o id_consulta(id da consulta).

        Retornos:
        - JsonResponse: Confirmação de deleção ou mensagem de erro.
        """
        id_consulta = kwargs.get('id_consulta')
        try:
            consulta = Consulta.objects.get(id_consulta=id_consulta)
            if not consulta:
                return JsonResponse("Não foi possível encontrar essa consulta.",status=404,safe=False)
            else:
                Consulta.objects.filter(id_consulta=id_consulta).delete()
            return JsonResponse("Consulta deletada com sucesso!",status=200,safe=False)   
        except Consulta.DoesNotExist:
            return JsonResponse("Essa consulta não existe.",status=404,safe=False)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)