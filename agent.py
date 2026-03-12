import os
from google.adk.agents.llm_agent import Agent

project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION")
datastore_id = os.getenv("GOOGLE_CLOUD_LOCATION")

def search_user_directory(search_query: str) -> str:
    """
    Searches the internal employee directory (synced from Entra ID) for users and groups.
    """
    try:
        client_options = (
            ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
            if LOCATION != "global"
            else None
        )
        client = discoveryengine.SearchServiceClient(client_options=client_options)

        serving_config = client.serving_config_path(
            project=project_id,
            location=location,
            data_store=datastore_id,
            serving_config="default_config",
        )

        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=search_query,
            page_size=3, # Limit results to keep context window manageable
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answer_count=1
                )
            ),
        )

        response = client.search(request)

        if not response.results:
            return f"Could nt find any information matching '{search_query}' in the directory."

        result_strings = []
        for i, result in enumerate(response.results):
            document_data = result.document.struct_data
            
            snippets = []
            if result.document.derived_struct_data:
                for segment in result.document.derived_struct_data.get("extractive_segments", []):
                    snippets.append(segment.get("content", ""))
            
            snippet_text = " ".join(snippets).strip()
            
            result_strings.append(f"Result {i+1}: Data: {document_data} | Snippet: {snippet_text}")

        return "\n\n".join(result_strings)

    except Exception as e:
        return f"An error occurred while querying the knowledge base: {str(e)}"

root_agent = Agent(
    name='entra_search',
    model='gemini-3.1-flash-preview',
    instruction='Answer user questions to the best of your knowledge',
    tools=[search_user_directory],
)
