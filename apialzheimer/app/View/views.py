from django.shortcuts import render
from app.Logica import modeloCNN  #para utilizar el método inteligente
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
import base64
import numpy as np
from io import BytesIO
import io
from PIL import Image
from tensorflow.keras.preprocessing import image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


CLASS_NAMES = ['Mild Demented', 'Moderate Demented', 'Non-Demented', 'Very Mild Demented']
#loaded_model = modeloCNN.modeloCNN.cargarRed("redCNN.h5")

class Clasificacion():

    @csrf_exempt
    def predict_image(request):
        if request.method == 'POST':
            try:
                # Decodificar el cuerpo de la solicitud
                data = json.loads(request.body.decode('utf-8'))

                # Verifica si los datos contienen la imagen en base64
                image_data = data.get('image_data', None)
                if not image_data:
                    return JsonResponse({"error": "No image data provided"}, status=400)

                # Eliminar la cabecera 'data:image/jpeg;base64,' si está presente
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]

                # Decodificar la imagen desde base64
                image_data = base64.b64decode(image_data)

                # Crear una imagen desde los datos binarios
                img = Image.open(io.BytesIO(image_data))

                # Redimensionar la imagen
                img = img.convert('RGB')
                img = img.resize((224, 224))  # Redimensionar la imagen
                
                img_array = image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array / 256.0  # Asegúrate de que esto esté de acuerdo con tu preprocesamiento
    
                # Ruta del modelo
                nombre = "C:/Users/jorge/OneDrive/Documentos/Python/ServidorDjango/apialzheimer/app/Logica/redCNN.h5"

                # Realizar la predicción con el modelo
                predicted_class_name = modeloCNN.modeloCNN.predecir_imagen(img_array, nombre)
                explicacion = modeloCNN.modeloCNN.explicar(img_array)
                def array_to_base64(arr):
                # Convertir la matriz (array) en una imagen
                    img = Image.fromarray(arr.astype(np.uint8))  # Asegúrate de que la matriz es de tipo uint8

                    # Guardar la imagen en un buffer en memoria
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")  # Guardamos la imagen en formato PNG
                    buffered.seek(0)

                    # Convertir la imagen en base64
                    img_base64 = base64.b64encode(buffered.read()).decode('utf-8')

                    return img_base64
                attributions_base64 = array_to_base64(explicacion)
                print("Imprimir matriz de explicacion")
                #print(explicacion)
                # Devolver la respuesta con la clase predicha
                return JsonResponse({"predicted_class": predicted_class_name, "Explicacion: ": attributions_base64})

            except Exception as e:
                # Manejo de errores
                return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({"error": "Method not allowed"}, status=405)
    

    
@api_view(['POST'])
def procesar_usuario(request):
    # Acceder directamente a los datos del body
    email = request.data.get('email')
    password = request.data.get('password')
    print(email)

    # Ahora puedes usar estos datos
    return Response({"email": email, "message": "Datos procesados correctamente"})