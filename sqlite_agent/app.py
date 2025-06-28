from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from db_tool import create_sample_db, sqlite_query_tool

# Ensure GOOGLE_API_KEY is set in your .env file
# Using a stable model name is a good practice.
llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0.0)

# Initialize the sample database
create_sample_db()

class DatabaseResponse(BaseModel):
  result : str
  tools_used : list[str] # Keep tools_used for consistency, though it will always be sqlite_query_tool

parser = PydanticOutputParser(pydantic_object=DatabaseResponse)


prompt = ChatPromptTemplate.from_messages(
  
  [
    (
      "system",
      """You are a SQLite database query assistant.
      Your primary function is to execute SQL queries against a SQLite database using the `sqlite_query_tool`.
      The database has a table named 'users' with columns: 'id', 'name', 'email'.
      
      Users will provide queries in the following template: "Query database for: [SQL query]".
      You MUST extract the SQL query from this template and pass it directly to the `sqlite_query_tool`.
      For example, if the user says "Query database for: SELECT * FROM users WHERE name = 'Alice'", you should call `sqlite_query_tool("SELECT * FROM users WHERE name = 'Alice'")`.
      
      Always answer the user query by providing the result from the `sqlite_query_tool` wrapped in the specified format.
      Provide no other text outside of the specified format.\n {format_instructions}
      """,
    ),
    
    ("placeholder","{chat_history}"),
    ("human","{query}"),
    ("placeholder","{agent_scratchpad}"),
    
  ]
).partial(format_instructions=parser.get_format_instructions())


tools = [sqlite_query_tool]

agent = create_tool_calling_agent(
  llm = llm,
  prompt= prompt,
  tools = tools
)

agent_executor = AgentExecutor(agent=agent,tools=tools, verbose=True)

query = input("What can I help you with regarding the database? ")


raw_response = agent_executor.invoke({"query":query})

try:
  # Get the raw output from the agent executor's response dictionary.
  raw_output = raw_response.get("output")
  
  # The model returns a string wrapped in markdown. We need to extract the JSON.
  if isinstance(raw_output, str) and raw_output.startswith('```json'):
      # Clean the string by removing the markdown code block fences.
      cleaned_json_string = raw_output.removeprefix('```json\n').removesuffix('```')
      # Parse the cleaned string using the Pydantic parser.
      structured_response = parser.parse(cleaned_json_string)
      print(structured_response)
  else:
      # If the output is not a markdown-wrapped string, print the raw output for debugging.
      print("The output is not in the expected markdown JSON format. Raw output:", raw_output)

except Exception as e:
  # Catch any other parsing errors and print the full raw response for inspection.
  print("Error parsing response:", e, "Raw Response -", raw_response)
