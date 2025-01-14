from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)  # Nombre del producto
    email = models.CharField(max_length=255)  # Precio
    password = models.CharField(max_length=255)  # Inventario

    def __str__(self):
        return self.name
    