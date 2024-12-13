
# -----------------------------------------------------------------------
# this is main
from dotenv import load_dotenv
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_core.tools import Tool
from todsop02 import GetPandas
from todsop03 import PlotAgent
from todsop04 import DataHandler
from datetime import datetime



class TyphoonAgent:
    def __init__(self):
        """Initialize the TyphoonAgent class."""
        load_dotenv()
        self.data_handler = DataHandler()

        # Load data
        dataset_path = os.getenv('DATASET_PATH')
        if not dataset_path:
            raise ValueError("DATASET_PATH environment variable is not set.")
        self.data_handler.load_data(dataset_path)

        # Initialize components
        self.llm = self.initialize_llm()
        self.memory = self.initialize_memory()
        self.tools = self.initialize_tools()
        self.agent = self.create_agent()
        self.agent_executor = self.create_agent_executor()

    def initialize_llm(self):
        """Set up the LLM with appropriate configuration."""
        return ChatOpenAI(
            base_url=os.getenv('TYPHOON_BASE_URL', 'https://api.opentyphoon.ai/v1'),
            model=os.getenv('TYPHOON_MODEL', 'typhoon-v1.5x-70b-instruct'),
            api_key=os.getenv('TYPHOON_API_KEY'),
            temperature=float(os.getenv('TEMPERATURE', 0.0)),
        )

    def initialize_memory(self):
        """Set up the memory for conversation history."""
        return ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def initialize_tools(self):
        """Initialize tools for the supervisor agent."""
        pandas_agent = GetPandas()
        plot_agent = PlotAgent()

        return [
            Tool(
                name='Pandas_agent',
                func=lambda user_input: pandas_agent.run(input_user=user_input),
                description="Analyze and visualize data within a Pandas DataFrame."
            ),
            Tool(
                name='Datetime_tool',
                func=self.get_current_datetime,
                description="Provides the current date and time."
            ),
            Tool(
                name='Plotting graph tool',
                func=lambda user_input: plot_agent.run(input_user=user_input),
                description='Use for plotting graphs.'
            )
        ]

    def get_current_datetime(self, _):
        """Return the current date and time formatted."""
        return f"Current datetime is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    def create_agent(self):
        """Create the React agent using LLM, tools, and prompt."""
        react_prompt = hub.pull(os.getenv('REACT_PROMPT', 'hwchase17/react-chat'))
        return create_react_agent(llm=self.llm, tools=self.tools, prompt=react_prompt)

    def create_agent_executor(self):
        """Set up the AgentExecutor with the React agent and tools."""
        return AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=int(os.getenv('MAX_ITERATIONS', 20)),
            handle_parsing_errors=True,
        )

    def process_query(self, user_input):
        """Process user input using the agent executor."""
        try:
            response = self.agent_executor.invoke({"input": user_input})
            print(response['output'])
        except Exception as e:
            print(f"An error occurred: {e}")

    def run(self):
        """Run the query loop to interact with the agent."""
        print("Welcome to the Typhoon Agent. Type 'stop agent' to exit.")
        while True:
            try:
                user_input = input("Enter your query: ")
                if user_input.lower() == "stop agent":
                    self.memory.clear()
                    print("Agent stopped, memory cleared.")
                    break
                self.process_query(user_input)
            except KeyboardInterrupt:
                print("\nAgent stopped. Goodbye!")
                break


if __name__ == "__main__":
    agent = TyphoonAgent()
    agent.run()
