from django.db import models


class Usuario(models.Model):

    id_usuario = models.BigAutoField(primary_key=True,null=False,blank=False)

    nome = models.CharField(max_length=500,null=False,blank=False)

    email = models.CharField(max_length=191,null=False,blank=False,unique=True)

    senha = models.CharField(max_length=200,null=False,blank=False)
   
class Pet(models.Model):

    id_pet = models.BigAutoField(primary_key=True,null=False,blank=False)

    nome = models.CharField(max_length=500,null=False,blank=False)

    especie = models.CharField(max_length=100,null=False,blank=False)

    idade = models.IntegerField(null=False,blank=False)

    dono_do_pet = models.ForeignKey(Usuario,on_delete=models.CASCADE)

class Veterinario(models.Model):

    id_veterinario = models.BigAutoField(primary_key=True,null=False,blank=False)

    nome = models.CharField(max_length=500,null=False,blank=False)

    especialidade = models.CharField(max_length=100,null=False,blank=False)

    email = models.CharField(max_length=191,null=False,blank=False,unique=True,db_index=False)

    senha = models.CharField(max_length=200,null=False,blank=False)

    

class Consulta(models.Model):

    id_consulta = models.BigAutoField(primary_key=True,null=False,blank=False)

    data_consulta = models.DateTimeField(null=True,blank=False)

    veterinario = models.ForeignKey(Veterinario,on_delete=models.CASCADE)

    pet = models.ForeignKey(Pet,on_delete=models.CASCADE)

    realizada = models.BooleanField(null=False,blank=False,default=False)