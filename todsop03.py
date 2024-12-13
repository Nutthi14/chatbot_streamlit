
# ----------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from todsop04 import DataHandler
from todsop_utils import CodeExecutor

load_dotenv()


class PlotAgent:
    ALLOWED_KEYWORDS = [
        'df', 'iloc', 'to_dict', 'mean', 'mode', 'std',
        'max', 'min', 'color', 'plot', 'unique', 'groupby'
    ]

    def __init__(self):
        """Initialize the PlotAgent class."""
        self.llm = self._initialize_llm()
        self.data_handler = DataHandler()
        self.df = self.data_handler.get_data()
        self.data_analysis_agent = self._create_agent()

    def _initialize_llm(self):
        """Initialize the language model with configuration."""
        return ChatOpenAI(
            base_url=os.getenv('PANDAS_BASE_URL', 'https://api.opentyphoon.ai/v1'),
            model=os.getenv('PANDAS_MODEL', 'typhoon-v1.5x-70b-instruct'),
            api_key=os.getenv('PLOT_API_KEY'),
            temperature=float(os.getenv('PANDAS_TEMPERATURE', 0))
        )

    def _create_agent(self):
        """Create a Pandas DataFrame agent with customized instructions."""
        suffix = (
            "You are working with a DataFrame. The exact column names are: "
            + ", ".join([f"'{col}'" for col in self.df.columns]) + ". "
            "Use df['column name'] syntax for column names with spaces. "
            "Generate Matplotlib plots in Python where applicable."
        )
        return create_pandas_dataframe_agent(
            llm=self.llm,
            df=self.df,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            suffix=suffix,
            verbose=True,
            allow_dangerous_code=True,
        )

    def _validate_columns(self, required_columns):
        """
        Ensure the DataFrame has the required columns for the operation.

        Args:
            required_columns (list): List of required column names.
        Raises:
            ValueError: If any required column is missing.
        """
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    def _extract_and_execute_code(self, response):
        """
        Extract and safely execute the code snippet from the agent's response.

        Args:
            response (dict): The agent's response containing the generated code.
        """
        code_snippet = CodeExecutor.extract_code_snippet(response.get('output', ''))
        if not code_snippet:
            raise ValueError("No valid code snippet generated by the agent.")
        print(f"Generated code:\n{code_snippet}")  # Debugging log

        CodeExecutor.execute_safe_code(
            code_snippet,
            self.ALLOWED_KEYWORDS,
            {'df': self.df, 'pd': pd, 'plt': plt}
        )

    def process_query(self, input_user: str):
        """
        Process user query using the DataFrame agent and execute the generated code.

        Args:
            input_user (str): User input query for visualization.
        """
        try:
            # Validate the columns dynamically based on the query
            if 'sale price' in input_user.lower():
                self._validate_columns(['sale price', 'country'])

            # Invoke the agent to process the query
            response = self.data_analysis_agent.invoke({"input": input_user})
            self._extract_and_execute_code(response)

        except Exception as e:
            print(f"An error occurred while processing the query: {e}")

    def run(self, input_user: str):
        """
        Run the agent for a specific visualization query.

        Args:
            input_user (str): User input query for visualization.
        """
        print(f"Processing query: {input_user}")
        self.process_query(input_user)


if __name__ == "__main__":
    agent = PlotAgent()
    agent.run(input_user='plot bar chart of sale price by country with unique color')