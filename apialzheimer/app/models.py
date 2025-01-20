from django.db import models

class Medico(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)  # Nombre del producto
    email = models.CharField(max_length=255, unique=True)  # Precio
    password = models.CharField(max_length=255)  # Inventario

    def __str__(self):
        return self.name
    
class Paciente(models.Model):
    id = models.AutoField(primary_key=True)
    dni = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    age = models.IntegerField()
    email = models.EmailField(max_length=255, unique=True)
    doctor = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name="pacientes")

    def __str__(self):
        return self.name

class Radiografia(models.Model):
    id = models.AutoField(primary_key=True)
    imagen_base64 = models.TextField()
    explicacion = models.TextField()
    probabilidad = models.TextField()
    fecha_subida = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="radiografias")

    def __str__(self):
        return self.usuario.name

