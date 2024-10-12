from django.test import TestCase, Client
from django.urls import reverse
from .models import Pet,Consulta,Veterinario, Usuario
import json
from datetime import datetime
from django.utils import timezone
import pytz
from django.contrib.auth.hashers import make_password,check_password 


#3 testes novos para fazer, 1 teste de numero inteiro negativo para create pet, 1 teste anterior para o update e verificar no update se o dono não existe.

class CreateUsuarioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('criar_usuario')
        self.data = {
            'nome':"Luis Carlos",
            'email':"Luis11@gmail.com",
            'senha':"@Luis12345"
        }
    def test_criar_usuario_com_sucesso(self):
        response = self.client.post(self.url,data=json.dumps(self.data),content_type='application/json')
        self.assertEqual(response.status_code,201,"O status é diferente.")

        

        usuario = Usuario.objects.get(email='Luis11@gmail.com')
        check_senha = check_password("@Luis12345",usuario.senha)

        self.assertEqual(usuario.nome,'Luis Carlos',"Nomes diferentes")
        self.assertEqual(usuario.email,'Luis11@gmail.com','emails diferentes')
        self.assertEqual(check_senha,True,'senhas diferentes')

    def test_tenta_criar_usuario_com_int(self):
        dados_errados = {
            'nome':"Luis Carlos",
            'email':12131231231,
            'senha': 123
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Tipo diferente")
    
    def test_tenta_criar_senha_apenas_minusculas(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"Luis123@gmail.com",
            "senha":"luiscarlosmacedo"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: senha foi aceita.")

    def test_tenta_criar_senha_apenas_maiusculas(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"Luis123@gmail.com",
            "senha":"LUISCARLOSMACEDO"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: senha foi aceita.")
    
    def test_tenta_criar_senha_apenas_especiais(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"Luis123@gmail.com",
            "senha":"@!@@##*#@!%¨&*"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: senha foi aceita.")

    def test_tenta_criar_email_caractere_nao_permitido(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"L!uis123@gmail.com",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")

    def test_tenta_criar_email_dois_pontos(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"Luis..123@gmail.com",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")

    def test_tenta_criar_email_com_espaco(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"Luis 123@gmail.com",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")

    def test_tenta_criar_email_sem_arroba(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"Luis123gmail.com",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")
    
    def test_tenta_criar_email_menos_3_caracteres_antes_arroba(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"13@gmail.com",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")

    def test_tenta_criar_email_mais_64_caracteres(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa1232323232@gmail.com",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")
    def test_tenta_criar_email_sem_ponto_no_dominio(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"edu121@gmail",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")
    def test_tenta_criar_email_fora_do_padrao(self):
        dados_errados = {
            "nome":"Luis Carlos",
            "email":"edu121@gmail.co",
            "senha":"Luis123#"
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Inesperado: email foi aceito.")
        
class GetUsuarioInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.url = reverse("info_usuario",kwargs={'id_usuario':self.usuario.id_usuario})
    
    def test_retorna_info_do_usuario_sucesso(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code,200,"Status diferentes.")

        self.assertEqual(self.usuario.nome,"Luis Carlos","nomes diferentes.")
        self.assertEqual(self.usuario.email,"Luis123@gmail.com","email diferentes.")
        self.assertEqual(self.usuario.senha,"123","senha diferente.")

    def test_tenta_retornar_usuario_inexistente(self):
        url_falsa = reverse("info_usuario",kwargs={'id_usuario':9999})
        
        response = self.client.get(url_falsa)
        
        self.assertEqual(response.status_code,404,"Usuário encontrado.")

class UpdateUsuarioInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='@Luis12345')
        self.url = reverse("atualiza_usuario",kwargs={'id_usuario':self.usuario.id_usuario})
        self.data = {
            'nome':"Luis Carlos",
            'email':"Luis11@gmail.com",
            'senha':"@Luis123456"
        }
    def test_atualize_informacoes_usuario_sucesso(self):
        response = self.client.put(self.url,data=self.data,content_type='application/json')
        usuario_atualizado = Usuario.objects.get(id_usuario=self.usuario.id_usuario)
        self.assertEqual(response.status_code,200,"Status diferentes.")

        check_senha = check_password("@Luis123456",usuario_atualizado.senha)
        self.assertEqual(check_senha,True,"senhas diferente")

    def test_tenta_atualizar_usuario_inexistente(self):
        url_falsa = reverse('atualiza_usuario',kwargs={'id_usuario':9999})
        response = self.client.put(url_falsa,data=self.data,content_type='application/json')
        self.assertEqual(response.status_code,404,"Resultado não esperado: Usuário foi encontrado")

class DeleteUsuarioInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.url = reverse("deleta_usuario",kwargs={'id_usuario':self.usuario.id_usuario})
        
       
    def test_deleta_informacoes_usuario_sucesso(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,200,"Usuário não foi deletado.")

    def test_tenta_deletar_usuario_inexistente(self):
        url_falsa = reverse('deleta_usuario',kwargs={'id_usuario':53})
        response = self.client.delete(url_falsa)
        self.assertEqual(response.status_code,404,"Resultado não esperado: Usuário foi encontrado")
        
           
class UsuarioMarcaConsultaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.vet = Veterinario.objects.create(nome='Doutor Francisco',especialidade='Cardiologista',email='Francisco123@gmail.com',senha='2321')
        self.url = reverse('marca_consulta',kwargs={'id_usuario': self.usuario.id_usuario})
        self.data = {
            'veterinario': self.vet.id_veterinario,
            'pet':self.pet.id_pet
        }
    def test_marca_consulta_sucesso(self):
        response = self.client.post(self.url,data=json.dumps(self.data),content_type='application/json')
        self.assertEqual(response.status_code,201,"Não foi possível cadastrar a consulta.")

        self.assertEqual(self.vet.email,"Francisco123@gmail.com","os emails não batem.")
        self.assertEqual(self.pet.dono_do_pet.email,"Luis123@gmail.com","os emails não batem.")

    def test_tenta_marcar_consulta_usuario_inexistente(self):
        url_falsa = reverse('marca_consulta',kwargs={'id_usuario': 9999})
        response = self.client.post(url_falsa,data=json.dumps(self.data),content_type='application/json')
        self.assertEqual(response.status_code,404,"Usuário foi encontrado")

    def test_tenta_marca_consulta_pet_inexistente(self):
        dados_errados = {
            'veterinario': self.vet.id_veterinario,
            'pet':9999
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,404,"Pet foi encontrado.")

    def test_tenta_marca_consulta_veterinario_inexistente(self):
        dados_errados = {
            'veterinario':9999,
            'pet':self.pet.id_pet
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,404,"Veterinario foi encontrado.")
    
class VizualizaConsultaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.vet = Veterinario.objects.create(nome='Doutor Francisco',especialidade='Cardiologista',email='Francisco123@gmail.com',senha='2321')
        self.consulta = Consulta.objects.create(data_consulta=timezone.now(),veterinario=self.vet,pet=self.pet,realizada=False)
        self.url = reverse('retorna_consulta',kwargs={'id_consulta':self.consulta.id_consulta})

    def test_retorna_informacao_consulta_sucesso(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code,200,"Não foi possível retornar informação.")

    def test_tenta_retornar_consulta_inexistente(self):
        url_falsa = reverse('retorna_consulta',kwargs={'id_consulta':9999})
        response = self.client.get(url_falsa)
        self.assertEqual(response.status_code,404,"Encontrou consulta")
    
class DeleteConsultaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.timezone = pytz.timezone("America/Fortaleza")
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.vet = Veterinario.objects.create(nome='Doutor Francisco',especialidade='Cardiologista',email='Francisco123@gmail.com',senha='2321')
        self.consulta = Consulta.objects.create(data_consulta=datetime.now().astimezone(self.timezone),veterinario=self.vet,pet=self.pet,realizada=False)
        self.url = reverse("deletar_consulta",kwargs={'id_consulta':self.consulta.id_consulta})
        
       
    def test_deleta_consulta_sucesso(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,200,"Consulta não foi deletada.")

    def test_tenta_deletar_consulta_inexistente(self):
        url_falsa = reverse('deletar_consulta',kwargs={'id_consulta':53})
        response = self.client.delete(url_falsa)
        self.assertEqual(response.status_code,404,"Resultado não esperado: Consulta foi encontrada")

class CreatePetViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('criar_pet')
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='#Luis12345')
        self.data = {
            'nome':"Jake",
            'especie':"canino",
            'idade':4,
            'dono_do_pet':1
        }
    def test_criar_usuario_com_sucesso(self):
        response = self.client.post(self.url,data=json.dumps(self.data),content_type='application/json')
        self.assertEqual(response.status_code,201,"Resultado não esperado: Os dados foram aceitos.")

        pet = Pet.objects.get(nome='Jake')
        self.assertEqual(pet.nome,'Jake',"Nomes diferentes")
        self.assertEqual(pet.especie,'canino','especies diferentes')
        self.assertEqual(pet.idade,4,'idades diferentes')
        self.assertEqual(pet.dono_do_pet.email,"Luis123@gmail.com",'donos diferentes')

    def test_tenta_criar_pet_com_especie_inteiro(self):
        dados_errados = {
            'nome':"Jake",
            'especie':12131231231,
            'idade': 123,
            'dono_do_pet':1
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Resultado não esperado: Os dados foram aceitos.")

    def test_tenta_criar_pet_com_idade_negativa(self):
        dados_errados = {
            'nome':"Jake",
            'especie':"Canina",
            'idade': -1,
            'dono_do_pet':self.usuario.id_usuario
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Resultado não esperado: idade negativa foi aceita.")

class GetPetInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.url = reverse("retorna_pet",kwargs={'id_pet':self.pet.id_pet})
    
    def test_retorna_info_do_pet_sucesso(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code,200,"Status diferentes.")

        self.assertEqual(self.usuario.nome,"Luis Carlos","nomes diferentes.")
        self.assertEqual(self.pet.nome,"Susie","nomes diferentes.")
        

    def test_tenta_retornar_pet_inexistente(self):
        url_falsa = reverse("retorna_pet",kwargs={'id_pet':9999})
        
        response = self.client.get(url_falsa)
        
        self.assertEqual(response.status_code,404,"Pet encontrado.")


class UpdatePetInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.url = reverse("atualiza_pet",kwargs={'id_pet':self.pet.id_pet})
        self.data = {
            'nome':"Susie",
            'especie':"canino",
            'idade':8,
            'dono_do_pet':self.usuario.id_usuario
        }
    def test_atualiza_informacoes_pet_sucesso(self):
        response = self.client.put(self.url,data=self.data,content_type='application/json')
        pet_atualizado = Pet.objects.get(nome=self.pet.nome)

        self.assertEqual(response.status_code,200,"Status diferentes.")
        self.assertEqual(pet_atualizado.especie,"canino","especie diferente")
        self.assertEqual(pet_atualizado.idade,8,'idades diferentes')
        self.assertEqual(pet_atualizado.nome,"Susie","nome diferente")

        self.assertEqual(pet_atualizado.dono_do_pet.id_usuario,self.usuario.id_usuario,"donos diferente")

    def test_tenta_atualizar_pet_inexistente(self):
        url_falsa = reverse('atualiza_pet',kwargs={'id_pet':9999})
        response = self.client.put(url_falsa,data=self.data,content_type='application/json')
        self.assertEqual(response.status_code,404,"Resultado não esperado: Pet foi encontrado")

    def test_tenta_atualizar_pet_com_idade_negativa(self):
        dados_errados = {
            'nome':"Jake",
            'especie':"Canina",
            'idade': -1,
            'dono_do_pet':self.usuario.id_usuario
        }
        response = self.client.put(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Resultado não esperado: idade negativa foi aceita.")

    def test_tenta_atualizar_pet_com_dono_inexistente(self):
        dados_errados = {
            'nome':"Jake",
            'especie':"Canina",
            'idade': 3,
            'dono_do_pet':9999
        }
        response = self.client.put(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,404,"Resultado não esperado: Dono encontrado.")

class DeletePetInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.url = reverse("deleta_pet",kwargs={'id_pet':self.pet.id_pet})
        
       
    def test_deleta_pet_sucesso(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,200,"Pet não foi deletado.")

    def test_tenta_deletar_pet_inexistente(self):
        url_falsa = reverse('deleta_pet',kwargs={'id_pet':9999})
        response = self.client.delete(url_falsa)
        self.assertEqual(response.status_code,404,"Resultado não esperado: Pet foi encontrado")

class CreateVeterinarioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('cadastra_veterinario')
        self.data = {
            'nome':"Doutor Francisco",
            'especialidade':"cardiologista",
            'email':"Fran1@gmail.com",
            'senha':"@Franciscco123"
        }
    def test_criar_veterinario_com_sucesso(self):
        response = self.client.post(self.url,data=json.dumps(self.data),content_type='application/json')
        self.assertEqual(response.status_code,201,"O status é diferente.")

        vet = Veterinario.objects.get(email="Fran1@gmail.com")
        check_senha = check_password("@Franciscco123",vet.senha)

        self.assertEqual(vet.nome,'Doutor Francisco',"Nomes diferentes")
        self.assertEqual(vet.especialidade,'cardiologista','especialidades diferentes')
        self.assertEqual(vet.email,"Fran1@gmail.com",'emails diferentes')
        self.assertEqual(check_senha,True,'senhas diferentes')

    def test_tenta_criar_veterinario_com_int(self):
        dados_errados = {
            'nome':"Doutor Francisco",
            'especialidade':'cardiologista',
            'email':"Fran1@gmail.com",
            'senha': 123
        }
        response = self.client.post(self.url,data=json.dumps(dados_errados),content_type='application/json')
        self.assertEqual(response.status_code,400,"Tipo diferente")


class GetVeterinarioInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.vet = Veterinario.objects.create(nome="Luis Carlos",especialidade='neurologista',email='Luis123@gmail.com',senha='123')
        self.url = reverse("retorna_veterinario",kwargs={'id_veterinario':self.vet.id_veterinario})
    
    def test_retorna_info_do_veterinario_sucesso(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code,200,"Status diferentes.")

        self.assertEqual(self.vet.nome,"Luis Carlos","nomes diferentes.")
        self.assertEqual(self.vet.especialidade,'neurologista','especialidades diferentes')
        self.assertEqual(self.vet.email,"Luis123@gmail.com","email diferentes.")
        self.assertEqual(self.vet.senha,"123","senha diferente.")

    def test_tenta_retornar_veterinario_inexistente(self):
        url_falsa = reverse("retorna_veterinario",kwargs={'id_veterinario':9999})
        
        response = self.client.get(url_falsa)
        
        self.assertEqual(response.status_code,404,"Veterinário encontrado.")


class UpdateVeterinarioInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.vet = Veterinario.objects.create(nome="Luis Carlos",especialidade='neurologista',email='Luis123@gmail.com',senha='123')
        self.url = reverse("atualiza_vet",kwargs={'id_veterinario':self.vet.id_veterinario})
        self.data = {
            'nome':"Luis Carlos",
            'especialidade':'neurologista',
            'email':"Luis11@gmail.com",
            'senha':"@Luis123456"
        }
    def test_atualize_informacoes_usuario_sucesso(self):
        response = self.client.put(self.url,data=self.data,content_type='application/json')
        vet_atualizado = Veterinario.objects.filter(id_veterinario=self.vet.id_veterinario).values('id_veterinario','nome','especialidade','email','senha').first()

        check_senha = check_password("@Luis123456",vet_atualizado['senha'])

        self.assertEqual(response.status_code,200,"Status diferentes.")

        self.assertEqual(vet_atualizado['nome'],"Luis Carlos",'nomes diferentes')
        self.assertEqual(vet_atualizado['especialidade'],'neurologista','especialidades diferentes')
        self.assertEqual(vet_atualizado['email'],"Luis11@gmail.com","email diferente")
        self.assertEqual(check_senha,True,'senhas diferentes')

    def test_tenta_atualizar_usuario_inexistente(self):
        url_falsa = reverse('atualiza_vet',kwargs={'id_veterinario':9999})
        response = self.client.put(url_falsa,data=self.data,content_type='application/json')
        self.assertEqual(response.status_code,404,"Resultado não esperado: Veterinário foi encontrado")

class DeleteVeterinarioInfoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.vet = Veterinario.objects.create(nome="Luis Carlos",especialidade='neurologista',email='Luis123@gmail.com',senha='123')
        self.url = reverse("deleta_vet",kwargs={'id_veterinario':self.vet.id_veterinario})
        
       
    def test_deleta_informacoes_veterinario_sucesso(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,200,"Veterinário não foi deletado.")

    def test_tenta_deletar_veterinario_inexistente(self):
        url_falsa = reverse('deleta_vet',kwargs={'id_veterinario':9999})
        response = self.client.delete(url_falsa)
        self.assertEqual(response.status_code,404,"Resultado não esperado: Veterinário foi encontrado")

class DefineHorarioConsultaViewTest(TestCase):
    def  setUp(self):
        self.client = Client()
        self.timezone = pytz.timezone('America/Fortaleza')
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.vet = Veterinario.objects.create(nome='Doutor Francisco',especialidade='Cardiologista',email='Francisco123@gmail.com',senha='2321')
        self.consulta = Consulta.objects.create(id_consulta=1,veterinario=self.vet,pet=self.pet,realizada=False)
        self.url = reverse('define_data_consulta',kwargs={'id_consulta':self.consulta.id_consulta})
        self.data = {
            'data_consulta': '2024-09-30T10:00:00Z'
        }
    
    def test_define_data_com_sucesso(self):
        response = self.client.put(self.url,data=json.dumps(self.data),content_type='application/json')
        consulta_atualizada = Consulta.objects.get(id_consulta=self.consulta.id_consulta)
        self.assertEqual(response.status_code,200,"Status diferentes")
        self.assertEqual(consulta_atualizada.data_consulta.isoformat(),"2024-09-30T10:00:00+00:00","Datas diferentes.")

    def test_tenta_definir_data_em_consulta_inexistente(self):
        url_falsa = reverse('define_data_consulta',kwargs={'id_consulta':99999})
        response = self.client.put(url_falsa,data=json.dumps(self.data),content_type='application/json')
        self.assertEqual(response.status_code,404,'Consulta foi achada.')

class DefineConsultaComoRealizadaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(nome="Luis Carlos",email='Luis123@gmail.com',senha='123')
        self.pet = Pet.objects.create(nome='Susie',especie='Canina',idade=7,dono_do_pet=self.usuario)
        self.vet = Veterinario.objects.create(nome='Doutor Francisco',especialidade='Cardiologista',email='Francisco123@gmail.com',senha='2321')
        self.consulta = Consulta.objects.create(id_consulta=1,veterinario=self.vet,pet=self.pet,realizada=False)
        self.url = reverse('realiza_consulta',kwargs={'id_consulta':self.consulta.id_consulta})
        self.data = {
            'realizada': True
        }
    def test_define_consulta_como_realizada_sucesso(self):
        response = self.client.put(self.url,data=json.dumps(self.data),content_type='application/json')
        consulta_realizada = Consulta.objects.get(id_consulta=self.consulta.id_consulta)
        self.assertEqual(response.status_code,200,"Não foi possível atualizar.")
        self.assertEqual(consulta_realizada.realizada,True,"O booleano não está definido como true.")

    def test_tenta_definir_realizada_em_consulta_inexistente(self):
        url_falsa = reverse('realiza_consulta',kwargs={'id_consulta':99999})
        response = self.client.put(url_falsa,data=json.dumps(self.data),content_type='application/json')
        self.assertEqual(response.status_code,404,'Consulta foi achada.')
    

