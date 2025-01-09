from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Desactiva la protección CSRF (solo para desarrollo o pruebas)
def manejar_post(request):
    if request.method == "POST":
        try:
            # Parsear datos del cuerpo de la solicitud
            datos = json.loads(request.body)
            respuesta = {
                "mensaje": "Datos recibidos correctamente",
                "datos": datos,
            }
            return JsonResponse(respuesta, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido"}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)
