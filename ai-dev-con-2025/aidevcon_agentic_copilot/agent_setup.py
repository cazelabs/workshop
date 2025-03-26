import os
from llama_index.core import VectorStoreIndex
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.core import SummaryIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.objects import ObjectIndex
from llama_index.core.node_parser import SentenceSplitter



def get_medical_prompt(medical_document_title):
    medical_prompt = f"""
                        You are a specialized agent designed to answer queries about {medical_document_title}'s document.
                        You are a specialized medical information agent. When analyzing {medical_document_title}'s documents, provide clear, direct answers covering treatment approaches, medication details, and risk factors.

                        For every user query:
                        First provide a concise treatment approach with specific steps and interventions
                        List all medications with their exact dosages, frequencies, durations, and administration routes
                        Follow with a dedicated seperate section names:RISK FACTORS, detailing relevant patient characteristics and conditions that affect outcomes
                        Include all relevant numerical values, percentages, and statistical data from the source
                        Present information in a straightforward, factual manner
                        Maintain clinical accuracy while using clear language
                        Organize responses logically with appropriate headings and subheadings
                        Include alternative treatment options when mentioned in the source
                        Note any special patient populations or exceptions
                        Highlight critical drug interactions or contraindications

                        Strip out generic medical disclaimers and consultation warnings. Focus solely on delivering precise, actionable information from the source document.
                        You must ALWAYS use at least one of the tools provided when answering a question; do NOT rely on prior knowledge.
                    """
    return medical_prompt
def get_patient_report_prompt(patient_report_title):
    patient_report_prompt = f"""\
                                You are a specialized agent designed to answer queries about {patient_report_title}'s document.
                                You are a specialized medical information agent. When analyzing {patient_report_title}'s documents, provide clear, direct answers covering treatment approaches, medication details, and risk factors.
                                For every user query :
                                First provide a concise treatment approach with specific steps and interventions
                                List all medications with their exact dosages, frequencies, durations, and administration routes
                                Follow with a dedicated seperate section named:RISK FACTORS, risk factors section detailing relevant patient characteristics and conditions that affect outcomes
                                Include all relevant numerical values, percentages, and statistical data from the source
                                Present information in a straightforward, factual manner
                                Maintain clinical accuracy while using clear language
                                Organize responses logically with appropriate headings and subheadings
                                Include alternative treatment options when mentioned in the source
                                Note any special patient populations or exceptions
                                Highlight critical drug interactions or contraindications
                                Strip out generic medical disclaimers and consultation warnings. Focus solely on delivering precise, actionable information from the source document.
                                You must ALWAYS use at least one of the tools provided when answering a question; do NOT rely on prior knowledge.
                            """
    return patient_report_prompt

def process_medical_documents(medical_document_titles, node_parser, med_doc_docs, llm):
    med_doc_nodes = []
    medical_agents = {}
    # Process medical documents
    for medical_document_title in medical_document_titles:
        med_nodes = node_parser.get_nodes_from_documents(med_doc_docs[medical_document_title])
        med_doc_nodes.extend(med_nodes)

        if not os.path.exists(f"./data/{medical_document_title}"):
            vector_index = VectorStoreIndex(med_nodes)
            vector_index.storage_context.persist(persist_dir=f"./data/{medical_document_title}")
        else:
            vector_index = load_index_from_storage(StorageContext.from_defaults(persist_dir=f"./data/{medical_document_title}"))

        if not os.path.exists(f"./data/{medical_document_title}_summary"):
            summary_index = SummaryIndex(med_nodes)
            summary_index.storage_context.persist(persist_dir=f"./data/{medical_document_title}_summary")
        else:
            summary_index = load_index_from_storage(StorageContext.from_defaults(persist_dir=f"./data/{medical_document_title}_summary"))
    

        # summary_index = SummaryIndex(med_nodes)
        vector_query_engine = vector_index.as_query_engine(llm=llm)
        summary_query_engine = summary_index.as_query_engine(llm=llm)

        document_query_engine_tools = [
            QueryEngineTool(
                                query_engine = vector_query_engine,
                                metadata = ToolMetadata(
                                                        name="vector_tool",
                                                        description=(f"""Useful for questions related to specific aspects of 
                                                                          {medical_document_title}'s document (e.g.)."""),
                                                    ),
                            ),
            QueryEngineTool(
                                query_engine = summary_query_engine,
                                metadata = ToolMetadata(
                                                            name="summary_tool",
                                                            description=(f"""Useful for any requests that require a detailed explanation of everything 
                                                                        regarding {medical_document_title}'s document. For questions about specific sections, '
                                                                        'please use the vector_tool."""
                                                            ),
                                                        ),
                            ),
            ]
        # Build the agent for med_doc
        agent = OpenAIAgent.from_tools(
                                        document_query_engine_tools,
                                        llm = llm,
                                        verbose = True,
                                        system_prompt = get_medical_prompt(medical_document_title)
                                      )

        medical_agents[medical_document_title] = agent
    return medical_agents

def process_patient_document(patient_report_titles, node_parser, patient_docs, llm):
    patient_doc_nodes = []
    patient_agents = {}
# Process patient documents
    for patient_report_title in patient_report_titles:
        patient_nodes = node_parser.get_nodes_from_documents(patient_docs[patient_report_title])
        patient_doc_nodes.extend(patient_nodes)

        if not os.path.exists(f"./data/{patient_report_title}"):
            vector_index = VectorStoreIndex(patient_nodes)
            vector_index.storage_context.persist(persist_dir=f"./data/{patient_report_title}")
        else:
            vector_index = load_index_from_storage(
                StorageContext.from_defaults(persist_dir=f"./data/{patient_report_title}")
            )

        summary_index = SummaryIndex(patient_nodes)
        vector_query_engine = vector_index.as_query_engine(llm=llm)
        summary_query_engine = summary_index.as_query_engine(llm=llm)

        patient_query_engine_tools = [
            QueryEngineTool(
                                query_engine=vector_query_engine,
                                metadata=ToolMetadata(
                                                        name="vector_tool",
                                                        description=(f"""Useful for questions related to specific aspects of the 
                                                                    {patient_report_title} patient description (e.g., age, ailment, preliminary diagnosis)."""
                                                                    ),
                                                    )
                            ),
            QueryEngineTool(
                                query_engine=summary_query_engine,
                                metadata=ToolMetadata(
                                                        name="summary_tool",
                                                        description=(f"Useful for any requests that require a holistic summary of EVERYTHING about {patient_report_title}'s patient description."
                                                                    ),
                                                     )
                            )
        ]
        
        # Build the agent for patient document
        agent = OpenAIAgent.from_tools(
                                        patient_query_engine_tools,
                                        llm=llm,
                                        verbose=True,
                                        system_prompt=get_patient_report_prompt(patient_report_title)
                                      )
        patient_agents[patient_report_title] = agent
    return patient_agents

def setup_agents_and_query_engines(medical_document_titles, patient_report_titles, med_doc_docs, patient_docs, llm):
    node_parser = SentenceSplitter()
    print("setup_agents_and_query_engines -  Start ")
    agents = {}
    medical_agents = process_medical_documents(medical_document_titles, node_parser, med_doc_docs, llm)
    patient_agents = process_patient_document(patient_report_titles, node_parser, patient_docs, llm)
    agents = {**medical_agents,**patient_agents}
    print("===========================    AGENTS  Start   ===========================")
    print(agents)
    print("===========================    AGENTS  Stop   ===========================")
    return agents

"""
    Define tools for each medical document and patient description agent.

    Args:
        medical_document_titles (list): List of medical document titles.
        patient_report_titles (list): List of patient document titles.
        agents (dict): Dictionary containing agents for each document.

    Returns:
        list: A list of tools for querying the documents.
"""
def define_tools_for_agents(medical_document_titles, patient_report_titles, agents):
    print("define_tools_for_agents - Start")
    all_tools = []

    # Process medical documents
    for medical_prompt in medical_document_titles:
        document_summary = (
                                f"This content contains the document of {medical_prompt}. Use "
                                f"this tool if you want to answer any questions about {medical_prompt}'s resume (e.g.).\n"
                           )
        document_tool = QueryEngineTool(
                                            query_engine=agents[medical_prompt],
                                            metadata=ToolMetadata(
                                                                    name=f"tool_{medical_prompt}",
                                                                    description=document_summary,
                                                                ),
                                        )
        all_tools.append(document_tool)

    # Process patient documents
    for patient_report_title in patient_report_titles:
        patient_summary = (
                                f"This content contains the patient description for {patient_report_title}. Use "
                                f"this tool if you want to answer any questions about {patient_report_title}'s job description (e.g., age, ailment, preliminary diagnosis).\n"
                        )
        patient_tool = QueryEngineTool(
                                            query_engine=agents[patient_report_title],
                                            metadata=ToolMetadata(
                                                                    name=f"tool_{patient_report_title}",
                                                                    description=patient_summary,
                                                                 )
                                       )
        all_tools.append(patient_tool)
    return all_tools

"""
    Initializes the top-level agent using the provided query engine tools.

    Args:
        query_engine_tools: A list of query engine tools to be used by the agent.

    Returns:
        top_agent: An OpenAIAgent instance configured to use the provided tools.
"""
def initialize_top_agent(all_tools):
    print(" initialize_top_agent- start")
    # Define an "object" index and retriever over the tools
    obj_index = ObjectIndex.from_objects(all_tools, index_cls=VectorStoreIndex)
    top_agent_prompt = """
                            You are an agent designed to answer queries about a set of medical documents and patient descriptions.
                            Please always use the tools provided to answer a question. Do not rely on prior knowledge.

                            For example:
                                - If the query is about a specific medical document (e.g., Anjali sharma age, ailment or preliminary diagnosis), use the corresponding document tool.
                                - If the query is about a specific patient description (e.g., Chest Pe guidelines, management and approach), use the corresponding patient tool.

                            Answer queries related to  medication  with:

                                - Full medication details with exact numerical dosages, timing, and routes
                                - Complete treatment protocols including all interventions
                                - Monitoring requirements and treatment duration
                                - Drug interactions and contraindications
                                - Patient-specific factors affecting treatment
                                - Safety information and complications

                            Answer queries related to  treatments with:
                                - Numerical values and units
                                - Exact timing and duration
                                - Dose adjustments and rationale
                                - Required monitoring
                                - Success criteria

                            Include comprehensive risk assessment for every query:
                                - Treatment-specific risks
                                - Drug interaction potential
                                - Patient risk factors
                                - Time-sensitive concerns
                                - Required monitoring
                            Provide direct responses based solely on document content. Present information clearly without any disclaimer statements or warnings about consulting healthcare professionals. Maintain focus on delivering precise clinical details and instructions.
                            Always refer to the tools when answering and ensure the response is based on the provided documents.
                        """
    # Create the top-level agent using the tools defined earlier
    top_agent = OpenAIAgent.from_tools(
                                            tool_retriever=obj_index.as_retriever(similarity_top_k=3),
                                            system_prompt=top_agent_prompt,
                                            verbose=True,
                                        )
    return top_agent