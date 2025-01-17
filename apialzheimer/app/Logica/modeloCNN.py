import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import pandas as pd
from app.Logica import modeloCNN
import pickle
import keras
from tf_explain.core.integrated_gradients import IntegratedGradients
from app.models import User, Radiografia
from django.shortcuts import get_object_or_404

modelo = None
target = None
certeza = None

class_names = ['Mild Demented', 'Moderate Demented', 'Non-Demented', 'Very Mild Demented']

class modeloCNN():
    
    def predecir_imagen(image_array, nombre):
        """
        Realiza la predicción de la clase de la imagen y su probabilidad.
        """
        print("Llega al metodo para predecir ")
        print(nombre)
        global modelo
        global target
        global certeza
        loaded_model = load_model(nombre)
        
        # Realizamos la predicción (probabilidades para todas las clases)
        predictions = loaded_model.predict(image_array)
        
        # Obtener la clase predicha (con mayor probabilidad)
        predicted_class = np.argmax(predictions, axis=1)[0]
        target = predicted_class
        
        # Obtener el nombre de la clase
        predicted_class_name = class_names[predicted_class]
        
        # Obtener la probabilidad de la clase predicha
        predicted_probability = predictions[0][predicted_class] * 100  # Multiplicamos por 100 para obtener el porcentaje
        certeza = predicted_probability
        
        modelo = loaded_model
        
        return predicted_class_name
    
    def explicar(img_array):
        explainer = IntegratedGradients()
        global modelo
        global target
        print("Despues de modelo explainer")
        
        explanations = explainer.explain(
            validation_data=(img_array, target),  # Pasar la imagen y la clase objetivo
            model=modelo,
            class_index=target  # Especificar la clase objetivo
        )
        return explanations

    def crearRadiografia(request):
        email = request.data.get('email')
        imagen64 = request.data.get('imagen64')
        explicacion = request.data.get('explicacion')

        usuario = get_object_or_404(User, email=email)
        if usuario != '' and imagen64 != '' and explicacion != '':
            radio = Radiografia(usuario = usuario, imagen_base64 = imagen64, explicacion = explicacion)
            radio.save()