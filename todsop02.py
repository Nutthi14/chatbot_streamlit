
# -----------------------------------------------------------------------------------------
import os
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from todsop04 import DataHandler
from todsop_utils import CodeExecutor

load_dotenv()


class GetPandas:
    ALLOWED_KEYWORDS = [
        'df', 'iloc', 'to_dict', 'mean', 'mode', 'std', 
        'max', 'min', 'color', 'plot', 'unique', 'groupby'
    ]

    def __init__(self):
        """Initialize the GetPandas class."""
        self.llm = self._initialize_llm()
        self.data_handler = DataHandler()
        self.df = self.data_handler.get_data()
        self.data_analysis_agent = self._create_agent()

    def _initialize_llm(self):
        """Initialize the language model."""
        return ChatOpenAI(
            base_url=os.getenv('PANDAS_BASE_URL', 'https://api.opentyphoon.ai/v1'),
            model=os.getenv('PANDAS_MODEL', 'typhoon-v1.5x-70b-instruct'),
            api_key=os.getenv('PANDAS_API_KEY'),
            temperature=float(os.getenv('PANDAS_TEMPERATURE', 0))
        )

    def _create_agent(self):
        """Create a Pandas DataFrame agent."""
        suffix = (
            "You are working with a DataFrame. The exact column names in this dataset are: "
            + ", ".join([f"'{col}'" for col in self.df.columns]) + ". "
            "Use df['column name'] syntax if column names contain spaces."
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
        Ensure the DataFrame has the necessary columns.
        
        Args:
            required_columns (list): List of required column names.
        Raises:
            ValueError: If any required column is missing.
        """
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    def _extract_code_snippet(self, response_output):
        """
        Extract a valid code snippet from the agent's output.

        Args:
            response_output (str): The raw output from the agent.
        Returns:
            str: The extracted code snippet.
        """
        # Assuming response output contains Python code directly
        return CodeExecutor.extract_code_snippet(response_output)

    def _execute_generated_code(self, code_snippet):
        """
        Safely execute the generated code snippet.

        Args:
            code_snippet (str): The code to execute.
        """
        CodeExecutor.execute_safe_code(
            code_snippet,
            self.ALLOWED_KEYWORDS,
            {'df': self.df, 'pd': pd}
        )

    def process_query(self, input_user: str):
        """
        Process user query using the DataFrame agent.

        Args:
            input_user (str): User input query for analysis.
        """
        try:
            print(f"Processing query: {input_user}")  # Logging input
            response = self.data_analysis_agent.invoke({"input": input_user})
            response_output = response.get('output', '')

            if not response_output:
                raise ValueError("The agent did not return any output.")

            print(f"Agent response:\n{response_output}")  # Logging response
            code_snippet = self._extract_code_snippet(response_output)

            if not code_snippet:
                raise ValueError("No valid code snippet extracted from the agent's response.")

            print(f"Generated code:\n{code_snippet}")  # Logging generated code
            self._execute_generated_code(code_snippet)

        except Exception as e:
            print(f"An error occurred: {e}")

    def run(self, input_user: str):
        """
        Run the agent for a specific query.

        Args:
            input_user (str): User input query for analysis or visualization.
        """
        self.process_query(input_user)


if __name__ == "__main__":
    agent = GetPandas()
    agent.run(input_user='plot bar chart of sale price by country with unique colors')
