import os
from google.adk.agents.llm_agent import Agent
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("ENGINE_LOCATION")
engine_id = os.getenv("ENGINE_ID")

def search_user_directory(search_query: str) -> str:
    """
    Searches the internal employee directory (synced from Entra ID) for users and groups.
    """
    try:
        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )
        client = discoveryengine.SearchServiceClient(client_options=client_options)

        serving_config = (
            f"projects/{project_id}/locations/{location}/collections/"
            f"default_collection/engines/{engine_id}/servingConfigs/default_search"
        )

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=search_query,
            page_size=3,
        )

        response = client.search(request)

        results = list(response.results)
        if len(results) == 0:
            return f"No directory results for '{search_query}'."

        output = []
        for i, result in enumerate(results):
            data = result.document.struct_data
            
            name = document_data.get("displayName", "Unknown")
            title = document_data.get("jobTitle", "Unknown")
            email = document_data.get("mail", "Unknown")
            dept = document_data.get("department", "Unknown")
            
            output.append(
                f"Result {i+1}:\n"
                f"Name: {name}\n"
                f"Title: {title}\n"
                f"Email: {email}\n"
                f"Department: {dept}"
            )

        return "\n\n".join(output)

    except Exception as e:
        return f"Search failed: {str(e)}"

root_agent = Agent(
    name='entra_search',
    model='gemini-2.5-flash',
    instruction='Answer user questions using the user directory.',
    tools=[search_user_directory],
)
