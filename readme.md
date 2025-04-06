# PetStore - API

## Descrição
A **PetStore** é uma API desenvolvida em padrões REST, que oferece funcionalidades de **cadastro, leitura, atualização e remoção** de usuários, pets, veterinários e consultas. A PetStore também conta com funções específicas para usuários e veterinários:

- Um usuário pode marcar uma consulta para o seu pet e escolher o veterinário responsável. Ele pode, posteriormente, visualizar as informações da consulta.
- Um veterinário pode visualizar consultas e atualizar informações, incluindo a data marcada e definir se a consulta foi realizada ou não.
  
### Segurança:
- A API realiza validação de e-mail e senha durante o cadastro e atualização de usuários e veterinários, auxiliando na autenticação e veracidade dos dados.
- A senha dos usuários é criptografada, garantindo a confidencialidade das informações.

---

## Requisitos

- **Docker** e **Docker Hub** instalados na máquina.
- **Python 3.9** e **pip** instalados (caso queira rodar a aplicação localmente).

---

## Passo a passo

### 1. Instalar Docker e Docker Hub

- Para instalar o Docker, siga as instruções oficiais: [Instalar Docker](https://docs.docker.com/get-docker/)
- Para criar sua conta no Docker Hub, acesse: [Docker Hub](https://hub.docker.com/)

### 2. Fazer login no Docker Hub

Execute o comando abaixo para realizar o login no Docker Hub:

```bash
docker login
```
### 3° Passo:
- Instale a imagem da aplicação com o seguinte comando:

```bash
docker pull luiscmacedoo/django-petstore
```
### 4° Passo:
- Crie o banco de dados dentro de um contêiner PostgreSQL.

#### a) Criar uma rede (network):

```bash
docker network create petstore-network
```
#### b ) Criação do banco de dados dentro de um container PostgreSQL: 
- Existem duas formas de fazer isso manualmente ou automaticamente:
  - Manual: Execute o container com o comando:
```
    docker run -d --name my-postgres -e POSTGRES_USER=<seu_usuario> -e POSTGRES_PASSWORD=<sua_senha> -p 5432:5432 
```
  - Acesse o container PostgreSQL com o comando: 
```
docker exec -it my-postgres psql -U postgres
```
  - E crie o banco de dados com a sintaxe SQL do PostgreSQL:
```
CREATE DATABASE petstore;
```
  - Automática: Crie o banco de dados com o comando:
```
docker run -d --name my-postgres -e POSTGRES_USER=<seu_usuario> -e POSTGRES_PASSWORD=<sua_senha> -e POSTGRES_DB=petstore -p 5432:5432 postgres
```
### 5º Passo:
- Rode o container Django com o comando:
```
docker run -d --name django-petstore --network petstore-network -e DB_HOST=<nome_do_container_postgresql> -e DB_NAME=petstore -e DB_USER=postgres -e DB_PASSWORD=<sua_senha> luiscmacedoo/django-petstore
```
- Verifique os logs com o comando:
```
docker logs django-petstore
```
### 6º Passo:
- Aplique as migrações da API ao banco de dados com o comando:
```
docker exec -it django-petstore python manage.py migrate
```
- Acesse a documentação oficial da API e teste suas funções via:
- http://localhost:8000/swagger/

# Guia de Configuração Local da API PetStore

Siga os passos abaixo para configurar e rodar o projeto localmente após baixá-lo do repositório.

## 1. Clonar o Repositório
Primeiro, clone o repositório para sua máquina local.

```bash
git clone <URL-do-repositorio>
cd <nome-do-repositorio>
```

## 2. Criar e Ativar o Ambiente Virtual
É necessário criar e ativar um ambiente virtual Python para evitar conflitos entre dependências.
### No Windows:
Para criar:
```
python -m venv .venv 
```
Para ativar:
```
.venv\Scripts\activate
```
### No macOS/Linux
Para criar: 
```
python3 -m venv .venv
```
Para ativar:
```
source .venv/bin/activate
```
## 3. Instalar as dependências
Com o ambiente virtual ativado, instale as dependências do projeto listadas no arquivo requirements.txt:
```
pip install -r requirements.txt
```
## 4. Configurar Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto. Este arquivo deve conter as variáveis de ambiente necessárias para o funcionamento da API, como configurações de banco de dados e chaves secretas.

Você pode se basear no arquivo de exemplo env.example (caso exista no repositório). Exemplo de .env:
```
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgres://usuario:senha@localhost:5432/nome-do-banco
```

Certifique-se de preencher corretamente as variáveis, especialmente a URL do banco de dados. 

## 5. Executar as Migrações do Banco de Dados
Após configurar o banco de dados e as variáveis de ambiente, rode as migrações para criar as tabelas necessárias no banco de dados.
```
python manage.py migrate
```
## 6. Rodar a Aplicação Localmente
Com todas as configurações prontas, você  pode iniciar o servidor local:
```
python manage.py runserver
```
A API estará disponível em http://127.0.0.1:8000/swagger/.

## 7. Testar a API com um agente(Opcional)
Caso deseje testar as rotas da API, você pode usar uma ferramenta como Insomnia ou Postman.

### Sinta-se livre para usar da API e fazer modifições se desejar! 😉
