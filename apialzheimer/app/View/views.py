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
CLASE = None
class Clasificacion:
    
    def predict_image(request):
        try:
            image_data = base64.b64decode(request)
            img = Image.open(io.BytesIO(image_data))
            img = img.convert('RGB')
            img = img.resize((224, 224)) 
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = img_array / 256.0 
            
            nombre = "C:/Users/Anthony/Desktop/redCNN.h5"
            predicted_class_name = modeloCNN.modeloCNN.predecir_imagen(img_array, nombre)
            print(predicted_class_name)
            explicacion = modeloCNN.modeloCNN.explicar(img_array)
            def array_to_base64(arr):
                img = Image.fromarray(arr.astype(np.uint8))
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                buffered.seek(0)
                img_base64 = base64.b64encode(buffered.read()).decode('utf-8')
                return img_base64
            attributions_base64 = array_to_base64(explicacion)
            return {"predicted_class": predicted_class_name, "Explicacion": attributions_base64}
        except Exception as e:
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

    @csrf_exempt
    @api_view(['POST'])
    def createPatient(request):
        try:
            dni = request.data.get('dni')
            name = request.data.get('name')
            gender = request.data.get('gender')
            age = request.data.get('age')
            email = request.data.get('email')
            medico_id = request.data.get('doctor')
            doctor = get_object_or_404(Medico, id=medico_id)
            paciente = Paciente(dni = dni, name = name, gender = gender, age = age, email = email, doctor = doctor)
            paciente.save()
            return Response({"message": "Paciente registrado correctamente"}, status=200)
        except Exception as e:
            return Response({"error": str(e)})

    @csrf_exempt
    @api_view(['GET'])
    def getPatients(request):
        try:
            doctor_id = request.query_params.get('id', None)
            if not doctor_id:
                return Response({"error": "El parámetro 'id' es requerido."}, status=400)

            patients = Paciente.objects.filter(doctor_id=doctor_id).values('id', 'dni', 'name', 'gender', 'age', 'email')
            return Response(patients, status=200)
        except Exception as e:
            return Response({"error": str(e)})  
        
        

    @staticmethod
    def crearRadiografia(request):
        usuario = request.get('usuario')
        imagen64 = request.get('imagen_base64')
        explicacion = request.get('explicacion')
        probabilidad = request.get('probabilidad')
        dementia_level = request.get('dementia_level')
        if usuario != '' and imagen64 != '' and explicacion != '':
            radio = Radiografia(usuario = usuario, imagen_base64 = imagen64, explicacion = explicacion, probabilidad = probabilidad, dementia_level = dementia_level)
            radio.save()

    @staticmethod
    @csrf_exempt
    @api_view(['POST'])
    def MakePrediction(request):
        global CLASE
        if request.method =='POST':
            foto = request.data.get("foto")
            id = request.data.get("id")
            resp = Clasificacion.predict_image(str(foto))
            pred = resp.get("predicted_class")
            grad = resp.get("Explicacion")
            CLASE = pred

            probabilidad = modeloCNN.certeza
            usuario = get_object_or_404(Paciente, id=id)
            radiograph = {"imagen_base64": foto, "explicacion": grad, "probabilidad": probabilidad, "usuario": usuario, "dementia_level": pred}
            Clasificacion.crearRadiografia(radiograph)
            return Response({"Radiografia": grad, "Prediccion": CLASE, "Probabilidad": probabilidad})
        
    @csrf_exempt
    @api_view(['GET'])
    def traerRadio(request):
        if request.method == 'GET':
            try:
                id = request.query_params.get('id', None)
                if not id:
                    return JsonResponse({"error": "Parámetro 'email' no proporcionado"}, status=400)

                usuario = get_object_or_404(Paciente, id=id)
                radiografias = Radiografia.objects.filter(usuario=usuario)
                if radiografias.exists():
                    datos = [
                        {
                            "id": r.id,
                            "imagen_base64": r.imagen_base64,
                            "explicacion": r.explicacion,
                            "fecha_subida": r.fecha_subida.strftime('%Y-%m-%d %H:%M:%S'),
                            "probabilidad": r.probabilidad,
                            "dementia_level": r.dementia_level,
                            "recomendacion": r.recomendacion if r.recomendacion else None
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
        

    @csrf_exempt
    @api_view(['POST'])
    def chatgpt(request):
        if request.method == 'POST':
            id = request.data.get('id')
            demencia = request.data.get('demencia')
            probabilidad = request.data.get('probabilidad')
            user_message = f'Tengo una radiografía cerebral y una imagen explicativa generada con gradiente integrado. Los píxeles blancos destacan las áreas clave que el modelo ha usado para su predicción y requieren especial atención médica, ya que pueden indicar deterioro cerebral. El modelo ha clasificado la imagen con un nivel de demencia de {probabilidad} con probabilidad del {demencia} de acierto. Genera un reporte explicando la importancia de las zonas resaltadas. Además, proporciona dos recomendaciones cortas de cuidados adaptadas a la clase de demencia predicha, enfocadas en mejorar la calidad de vida del paciente. El reporte debe ser claro, técnico pero comprensible, sin títulos ni encabezados, en un solo párrafo de 175 palabras.'
            print(user_message)
            ref = modeloCNN.modeloCNN.solicitudIA(user_message)
            radiography = get_object_or_404(Radiografia, id=id)
            radiography.recomendacion = ref
            radiography.save()
            return Response({'Respuesta': ref})