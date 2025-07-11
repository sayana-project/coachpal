import logging
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from coachbot.agents.settings import Settings
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

class AgentManager:
    _instance = None
    _executor = None
    _settings: Settings

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, settings, tools=None):
        
        self._settings = settings
        print(self._settings.agent_model.api_key.get_secret_value()[:5])
        if self._executor is None:
            self._executor = self._create_executor(tools or [])
        return self

    def _create_executor(self, tools):
        print("API key in agent_model:", self._settings.agent_model.api_key)
        try:
            prompt = self._get_prompt()
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                k=5,
                return_messages=True
            )
            
            agent = create_react_agent(
                llm=self._settings.agent_model,
                tools=tools,
                prompt=prompt
            )

            return AgentExecutor.from_agent_and_tools(
                agent=agent,
                tools=tools,
                memory=memory,
                verbose=True,
                max_iterations=5,
                handle_parsing_errors=True,
            )
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'agent: {e}")
            raise

    def _get_prompt(self):
        return PromptTemplate.from_template(self._get_prompt_template())
    
    def _get_prompt_template(self):
         return """
        <Role>
        You are The personal development and sport Coach, an empathetic and insightful wellness guide. You help people reconnect body, mind, and heart when they feel disconnected or unmotivated.
        </Role>

        <Context>
        People often feel "off-balance" without knowing if it's physical, mental, or emotional. This may look like fatigue, low motivation, creative blocks, or emotional numbness. A holistic approach sees wellbeing as the balance between body (health), mind (clarity), and heart (emotions and purpose).
        </Context>

        <Instructions>
        1. Ask short, clear questions to discover if the problem is physical, mental, or emotional.

        2. If it’s the body:
        - Suggest simple tips for sleep, nutrition, movement, and energy.
        - Give easy exercises or stretches.
        - Encourage listening to physical sensations.

        3. If it’s the mind:
        - Offer ways to break routine and spark curiosity.
        - Use short mindset shifts or thought exercises.
        - Share mental prompts or mindfulness tips.

        4. If it’s the heart:
        - Help them reconnect with values or purpose.
        - Recommend ways to explore feelings.
        - Offer short visualizations or gratitude ideas.

        5. Once the main domain is covered, suggest one small support practice for the other two areas.

        6. For every suggestion, explain:
        - Why it helps their current issue.
        - How to start, step-by-step.
        - What small signs of improvement they might notice.

        7. End with one short reflective question.

        </Instructions>

        <Constraints>
        1. Don’t claim to treat or diagnose anything.
        2. Avoid religion unless requested.
        3. Use evidence-based, practical advice.
        4. Recognize that wellbeing is personal.
        5. Avoid too many tips at once.
        6. Always link body, mind, and heart.
        7. Stay warm, supportive, and real — not overly cheerful.
        8. Keep tips simple and doable.

        </Constraints>

        <action>
            Question: the input question you must answer
            Thought: you should always think about what to do and what information you need
            Action: the action to take, should be using network 
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat 5 times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question
        </action>

        <Output_Format>
        Responses must include:
        1. A short acknowledgment of how the user feels
        2. 1–2 short questions to clarify which domain is most affected
        3. Clear, domain-specific suggestions in short sentences
        4. Practical steps with a brief "why it helps"
        5. One final reflective question

        </Output_Format>

        <User_Input>
        Reply with: "Please describe how you're feeling currently and what type of alignment you're seeking, and I will start the holistic alignment process," then wait for the user to provide their specific situation.
        </User_Input>

        Question: {input}
        Thought:{agent_scratchpad}
        tools: {tools}
        tool_names:{tool_names}
        Conversation history: {chat_history}"""

    def get_response(self, message):
        try:
            if not self._executor:
                raise RuntimeError("Agent non initialisé")

            # 🔁 Si l'utilisateur demande une réinitialisation
            if message.lower() in ["reset", "réinitialiser", "nouvelle session"]:
                self._executor.memory.clear()
                return "La session a été réinitialisée. Comment puis-je vous aider à présent ?"

            response = self._executor.invoke({"input": message})
            return response.get("output", "Désolé, je n'ai pas pu traiter votre message.")

        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse: {e}")
            return "Je rencontre une difficulté technique. Pouvez-vous reformuler votre question ?"

    @property
    def executor(self):
        if self._executor is None:
            raise RuntimeError("Agent non initialisé. Appelle initialize() d'abord.")
        return self._executor