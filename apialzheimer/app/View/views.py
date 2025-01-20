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
from app.models import Paciente, Radiografia, Medico
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

    @csrf_exempt
    @api_view(['POST'])
    def procesar_usuario(request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            user = Medico.objects.get(email=email, password=password)
            return Response({ "message": user.id , "name": user.name, "success": True } , status=200)

        except Medico.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
                
    @csrf_exempt
    @api_view(['POST'])
    def Crear_Usuario(request):
        try:
            name = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            
            usuario = Medico(name = name, email = email, password = password)
            usuario.save()

            return Response({"message: ": "Ok" }, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


    @staticmethod
    def crearRadiografia(request):
        usuario = request.get('usuario')
        imagen64 = request.get('imagen_base64')
        explicacion = request.get('explicacion')
        probabilidad = request.get('probabilidad')
        if usuario != '' and imagen64 != '' and explicacion != '':
            radio = Radiografia(usuario = usuario, imagen_base64 = imagen64, explicacion = explicacion, probabilidad = probabilidad)
            radio.save()

    @staticmethod
    @csrf_exempt
    @api_view(['POST'])
    def MakePrediction(request):
        #clasificacion = Clasificacion()
        global CLASE
        if request.method =='POST':
            foto = request.data.get("foto")
            resp = Clasificacion.predict_image(str(foto))
            print('Se realiza la prediccion')
            print('-------------------------')
            print(resp)
            print('-------------------------')
            pred = resp.get("predicted_class")
            grad = resp.get("Explicacion")
            CLASE = pred
            probabilidad = modeloCNN.certeza
            email = request.data.get("email")
            usuario = get_object_or_404(Paciente, email=email)
            radiograph = {"imagen_base64": foto, "explicacion": grad, "probabilidad": probabilidad, "usuario": usuario}
            Clasificacion.crearRadiografia(radiograph)
            return Response({"Radiografia": grad, "Prediccion": CLASE, "Probabilidad": probabilidad})

        
    @csrf_exempt
    @api_view(['GET'])
    def traerRadio(request):
        if request.method == 'GET':
            try:
                email = request.query_params.get('email', None)
                if not email:
                    return JsonResponse({"error": "Parámetro 'email' no proporcionado"}, status=400)

                usuario = get_object_or_404(Paciente, email=email)
                radiografias = Radiografia.objects.filter(usuario=usuario)
                if radiografias.exists():
                    datos = [
                        {
                            "imagen_base64": r.imagen_base64,
                            "explicacion": r.explicacion,
                            "fecha_subida": r.fecha_subida.strftime('%Y-%m-%d %H:%M:%S'),
                            "probabilidad": r.probabilidad
                        }
                        for r in radiografias
                    ]
                    return JsonResponse(datos, safe=False, status=200)
                else:
                    return JsonResponse({"error": "No se encontraron radiografías para este usuario"}, status=404)

            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
            
    @csrf_exempt
    @api_view(['PUT'])
    def editProfile(request):
        try:
            print(request.data)
            email = request.data.get('emailFromLocalStorage')
            new_email = request.data.get('email')
            name = request.data.get('username')
            user = get_object_or_404(Medico, email=email)
            if new_email and new_email != email:
                user.email = new_email
            user.name = name
            user.save()
            return Response({"username": user.name, "email": user.email}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    @csrf_exempt
    @api_view(['POST'])
    def registerPatient(request):
        try:
            dni = request.data.get('dni')
            name = request.data.get('name')
            gender = request.data.get('gender')
            age = request.data.get('age')
            email = request.data.get('email')
            doctor_email = request.data.get('doctor_email')
            doctor = get_object_or_404(Medico, email=doctor_email)
            paciente = Paciente(dni = dni, name = name, gender = gender, age = age, email = email, doctor = doctor)
            paciente.save()
            return Response({"message": "Usuario registrado correctamente"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    @csrf_exempt
    @api_view(['PUT'])
    def editPassword(request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            user = get_object_or_404(Medico, email=email)
            if password:
                user.password = password
            user.save()
            return Response({"message": "Usuario actualizado correctamente"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    @csrf_exempt
    @api_view(['GET'])
    def getProfile(request):
        try:
            email = request.query_params.get('email', None)
            if not email:
                return Response({"error": "Parámetro 'email' no proporcionado"}, status=400)
            user = get_object_or_404(Medico, email=email)
            return Response({"username": user.name, "email": user.email}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

    