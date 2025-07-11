import os
from langchain_deepseek import ChatDeepSeek
from pathlib import Path
import environ, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

sk_key = env("DEEPSEEK_API_KEY")
class Settings:
    def __init__(self):
        self.agent_model = ChatDeepSeek(
            temperature=0.7,
            model="deepseek-chat",
            api_key=sk_key
        )

        # 🔍 Optionnel : afficher la clé pour debug
        print("✅ Clé DeepSeek active :", self.agent_model.api_key.get_secret_value()[:10] + "...")