import json
import logging
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from coachbot.ai.agent import AgentManager
from coachbot.agents.settings import Settings  

logger = logging.getLogger(__name__)

# Initialisation globale (à optimiser en production)
try:
    settings = Settings()
    agent_manager = AgentManager().initialize(settings=settings)
except Exception as e:
    logger.error(f"Erreur d'initialisation de l'agent: {e}")
    agent_manager = None

class CoachChatView(View):
    def get(self, request):
        """Affiche la page de chat"""
        return render(request, "coachbot/chat.html")

    @method_decorator(csrf_exempt)
    def post(self, request):
        """Traite les messages du chat"""
        try:
            if not agent_manager:
                return JsonResponse({
                    "response": "Service temporairement indisponible.",
                    "error": True
                })

            # Récupération du message
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                message = data.get('message', '')
            else:
                message = request.POST.get('message', '')

            if not message.strip():
                return JsonResponse({
                    "response": "Veuillez saisir un message.",
                    "error": True
                })

            # Génération de la réponse
            response = agent_manager.get_response(message)
            
            return JsonResponse({
                "response": response,
                "error": False
            })

        except Exception as e:
            logger.error(f"Erreur dans CoachChatView: {e}")
            return JsonResponse({
                "response": "Une erreur s'est produite. Veuillez réessayer.",
                "error": True
            })
