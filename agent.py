import os
from google.adk.agents.llm_agent import Agent
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("ENGINE_LOCATION")
engine_id = os.getenv("ENGINE_ID")

def search_user_directory(query: str) -> str:
    """
    Searches the internal employee directory (synced from Entra ID) for users and groups.
    """
    try:
        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )
        client = discoveryengine.AssistantServiceClient(client_options=client_options)

        request = discoveryengine.StreamAssistRequest(
            name=client.assistant_path(
                project=project_id,
                location=location,
                collection="default_collection",
                engine=engine_id,
                assistant="default_assistant",
            ),
            query=discoveryengine.Query(text=query)
        )

        stream = client.stream_assist(request=request)

        output = []
        for response in stream:
            output.append(str(response))
        
        return "\n".join(output)

    except Exception as e:
        return f"Search failed: {str(e)}"

root_agent = Agent(
    name='entra_search',
    model='gemini-2.5-flash',
    instruction='Answer user questions using the user directory.',
    tools=[search_user_directory],
)
