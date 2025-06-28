from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool


# Ensure GOOGLE_API_KEY is set in your .env file
# Using a stable model name is a good practice.
llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0.0)

class ResearchResponse(BaseModel):
  topic : str
  summary : str
  sources : list[str]
  tools_used : list[str]

parser = PydanticOutputParser(pydantic_object=ResearchResponse)


prompt = ChatPromptTemplate.from_messages(
  
  [
    (
      "system",
      """You are a research assistant that will help generate a research paper.
      Always use the provided tools (search, wiki_tool) to gather information. If the user asks to save information, use the `save_text_to_file` tool with the generated `summary` as the `data` argument.
      Answer the user query and wrap the output in this format and provide no other text\n {format_instructions}
      """,
    ),
    
    ("placeholder","{chat_history}"),
    ("human","{query}"),
    ("placeholder","{agent_scratchpad}"),
    
  ]
).partial(format_instructions=parser.get_format_instructions())


tools = [search_tool, wiki_tool, save_tool]

agent = create_tool_calling_agent(
  llm = llm,
  prompt= prompt,
  tools = tools
)

agent_executor = AgentExecutor(agent=agent,tools=tools, verbose=True)

query = input("what can i help you reasearch? ")


raw_response = agent_executor.invoke({"query":query})

# --- CORRECTED CODE BLOCK ---
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
# --- END CORRECTED CODE BLOCK ---
