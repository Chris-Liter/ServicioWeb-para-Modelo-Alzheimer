import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import pandas as pd
from app.Logica import modeloCNN
import pickle
import keras
from tf_explain.core.integrated_gradients import IntegratedGradients  # Asegúrate de tener el módulo correcto para IntegratedGradients

 
modelo = None
target = None
class modeloCNN():
    class_names = ['Mild Demented', 'Moderate Demented', 'Non-Demented', 'Very Mild Demented']
            #Función para cargar red neuronal 
    # def cargarRed():  
    #     model = load_model("/ServidorDjango/apialzheimer/apialzheimer/modelo/redCNN.h5")
    #     print("Red Neuronal Cargada desde Archivo") 
    #     return model


    # def cargar_imagen(self, image_path, target_size=(224, 224)):
    #         """
    #         Cargar y preprocesar una imagen para la predicción.
    #         """
    #         img = image.load_img(image_path, target_size=target_size)
    #         img_array = image.img_to_array(img)
    #         img_array = np.expand_dims(img_array, axis=0)  # Añadir dimensión de batch
    #         img_array = img_array / 256.0  # Normalizar como se hizo durante el entrenamiento
    #         return img_array
    

    def predecir_imagen(image_array, nombre):
        """
        Realiza la predicción de la clase de la imagen.
        """
        print("Llega al metodo para predecir ")
        print(nombre)
        global modelo
        global target
        loaded_model = load_model(nombre)
        
        predictions = loaded_model.predict(image_array)
    
        # Obtener la clase predicha
        predicted_class = np.argmax(predictions, axis=1)[0]
        target = predicted_class
        # Obtener el nombre de la clase
        class_names = ['Mild Demented', 'Moderate Demented', 'Non-Demented', 'Very Mild Demented']
        predicted_class_name = class_names[predicted_class]
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