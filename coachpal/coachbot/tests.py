from django.test import TestCase
from coachbot.agents.settings import Settings
from coachbot.ai.agent import AgentManager


class AIAgentTest(TestCase):
    def setUp(self):
        self.settings = Settings()
        self.agent = AgentManager().initialize(self.settings)

    def test_agent_bonjour(self):
        """Teste si l'agent IA répond à 'Bonjour'"""
        prompt = "Bonjour"
        response = self.agent.get_response(prompt)

        print("\n🧪 Prompt envoyé :", prompt)
        print("🤖 Réponse IA :", response)

        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0, "La réponse est vide")