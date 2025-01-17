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
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models import User, Radiografia
from django.shortcuts import get_object_or_404



CLASS_NAMES = ['Mild Demented', 'Moderate Demented', 'Non-Demented', 'Very Mild Demented']
#loaded_model = modeloCNN.modeloCNN.cargarRed("redCNN.h5")
CLASE = None
class Clasificacion:
    
    #@staticmethod
    def predict_image(request):
        try:
            #data = json.loads(request.body.decode('utf-8'))
            # Verifica si los datos contienen la imagen en base64
            #image_data = request.data.get("foto")
            #print(image_data)
            #if not image_data:
            #    return {"error": "No image data provided"}
            # Eliminar la cabecera 'data:image/jpeg;base64,' si está presente
            #if request.startswith('data:image'):
            #    request = request.split(',')[1]
            # Decodificar la imagen desde base64
            image_data = base64.b64decode(request)
            
            # Crear una imagen desde los datos binarios
            img = Image.open(io.BytesIO(image_data))
            # Redimensionar la imagen
            img = img.convert('RGB')
            img = img.resize((224, 224))  # Redimensionar la imagen
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 256.0  # Asegúrate de que esto esté de acuerdo con tu preprocesamiento
            
            # Ruta del modelo
            nombre = "C:/Users/jorge/OneDrive/Documentos/Python/modelo/redCNN.h5"
            # Realizar la predicción con el modelo
            predicted_class_name = modeloCNN.modeloCNN.predecir_imagen(img_array, nombre)
            print(predicted_class_name)
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
            return {"predicted_class": predicted_class_name, "Explicacion": attributions_base64}
        except Exception as e:
            # Manejo de errores
            return {"error": str(e)}

        

        
    #@staticmethod

    @csrf_exempt
    @api_view(['POST'])
    def procesar_usuario(request):
        try:
            # Acceder directamente a los datos del body
            email = request.data.get('email')
            password = request.data.get('password')

            # Buscar usuario en la base de datos
            user = User.objects.get(email=email, password=password)
            # Devolver respuesta si el usuario existe
            return Response({ "message": email, "success": True } , status=200)

        except User.DoesNotExist:
            # Manejar cuando el usuario no existe
            return Response({"error": "Usuario no encontrado"}, status=404)

        except Exception as e:
            # Manejar cualquier otra excepción
            return Response({"error": str(e)}, status=500)

    # Ahora puedes usar estos datos


                
    @csrf_exempt
    @api_view(['POST'])
    def Crear_Usuario(request):

        name = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        usuario = User(name = name, email = email, password = password)
        usuario.save()
        return Response({"name: ": name, "email: ": email, "password: ": password })


    @staticmethod
    def crearRadiografia(request):
        email = request.get('email')
        imagen64 = request.get('imagen64')
        explicacion = request.get('explicacion')

        usuario = get_object_or_404(User, email=email)
        if usuario != '' and imagen64 != '' and explicacion != '':
            radio = Radiografia(usuario = usuario, imagen_base64 = imagen64, explicacion = explicacion)
            radio.save()

    @staticmethod
    @csrf_exempt
    @api_view(['POST'])
    def MakePrediction(request):
        #clasificacion = Clasificacion()
        global CLASE
        if request.method =='POST':
            foto = request.data.get("foto")
            js = {"foto": foto }

            #json_data = json.dumps(js)
            email = request.data.get("email")
            #print(json_data)
            resp = Clasificacion.predict_image(str(foto))
            print('Se realiza la prediccion')
            
            print('-------------------------')
            print(resp)
            print('-------------------------')
            pred = resp.get("predicted_class")
            grad = resp.get("Explicacion")
            CLASE = pred
            radiograph = {"email": email, "imagen64": foto, "explicacion": grad}
            clasificacion.crearRadiografia(radiograph)
            return Response({"Radiografia": grad, "Prediccion": CLASE})

        
    @csrf_exempt
    @api_view(['GET'])
    def traerRadio(request):
        if request.method == 'GET':
            try:
                email = request.query_params.get('email', None)
                if not email:
                    return JsonResponse({"error": "Parámetro 'email' no proporcionado"}, status=400)

                usuario = get_object_or_404(User, email=email)
                radiografias = Radiografia.objects.filter(usuario=usuario)

                if radiografias.exists():
                    # Convertimos las radiografías a una lista de diccionarios
                    datos = [
                        {
                            "imagen_base64": r.imagen_base64,
                            "explicacion": r.explicacion,
                            "fecha_subida": r.fecha_subida.strftime('%Y-%m-%d %H:%M:%S'),
                        }
                        for r in radiografias
                    ]
                    return JsonResponse({"Info": datos}, status=200)
                else:
                    return JsonResponse({"error": "No se encontraron radiografías para este usuario"}, status=404)

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
