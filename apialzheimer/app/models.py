from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)  # Nombre del producto
    email = models.CharField(max_length=255, unique=True)  # Precio
    password = models.CharField(max_length=255)  # Inventario

    def __str__(self):
        return self.name
    

class Radiografia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="radiografias")
    imagen_base64 = models.TextField()  # Para almacenar la imagen en Base64
    explicacion = models.TextField()
    probabilidad = models.TextField()
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Radiografía de {self.usuario.nombre} subida el {self.fecha_subida}"


