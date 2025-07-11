import os
from langchain_deepseek import ChatDeepSeek

class Settings:
    def __init__(self):
        # 🟡 Clé codée en dur pour test local uniquement
        self.agent_model = ChatDeepSeek(
            temperature=0.7,
            model="deepseek-chat",
            api_key=self.agent_model.api_key.get_secret_value()  # Remplace par ta vraie clé
        )

        # 🔍 Optionnel : afficher la clé pour debug
        print("✅ Clé DeepSeek active :", self.agent_model.api_key.get_secret_value()[:10] + "...")