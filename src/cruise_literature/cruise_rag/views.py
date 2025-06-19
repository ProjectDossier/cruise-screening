# Create your views here.
from langchain_elasticsearch import ElasticsearchStore
from elasticsearch import Elasticsearch

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.chains import RetrievalQA
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from literature_review.models import LiteratureReview
from .models import LLMConversation
import requests
import json
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Initialize Elasticsearch and embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
es_connection = Elasticsearch("http://localhost:9200")


def review_id_to_index(review_id):
    return f"review_{review_id}_index"


def get_id_for_a_page_by_metadata(title, page, doi):
    return f"{title}_{page}_{doi}"


def get_id_for_a_page(paper_page):
    return get_id_for_a_page_by_metadata(
        paper_page.metadata["title"],
        paper_page.metadata["page"],
        paper_page.metadata["doi"],
    )


def download_pdf(pdf_url):
    logger.info(f"Downloading PDF from {pdf_url}")
    try:
        temp_file = NamedTemporaryFile()
        response = requests.get(pdf_url, verify=False)
        if response.status_code == 200:
            temp_file.write(response.content)
            temp_file.flush()
            logger.info(f"PDF downloaded to {temp_file.name}")
            return temp_file
        else:
            logger.error(f"Failed to download PDF: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        return None


def add_paper_to_elasticsearch_index(review_id, paper):
    """
    Function to index embeddings.
    """
    logger.info("Adding paper to Elasticsearch index for RAG...")
    logger.info(f"PDF: {paper.get('pdf', 'No PDF')}")

    paper_pages = []

    try:
        if "pdf" in paper and paper["pdf"]:
            pdf_url = paper["pdf"]
            temp_pdf_file = download_pdf(pdf_url)
            if temp_pdf_file:
                # Load the PDF and extract text
                pdf_loader = PyPDFLoader(temp_pdf_file.name)
                paper_pages = pdf_loader.load_and_split()

                for paper_page in paper_pages:
                    paper_page.metadata["title"] = paper["title"]
                    paper_page.metadata["authors"] = paper["authors"]
                    paper_page.metadata["doi"] = paper["doi"]
                    paper_page.metadata["abstract"] = paper["abstract"]

                logger.info(f"Loaded {len(paper_pages)} pages from PDF.")
            else:
                logger.info("No PDF file found or failed to download.")
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")

    logger.info(paper)

    if len(paper_pages) == 0:
        logger.info("No PDF file found, using abstract instead.")

        content = paper["abstract"] if "abstract" in paper else None

        if not content:
            logger.info("No abstract found.")
            content = paper["abstract"] if "snippet" in paper else None

        if not content:
            logger.info("No snippet found, stop.")
            return

        paper_pages = [
            Document(
                page_content=content,
                metadata={
                    "title": paper["title"] if "title" in paper else "",
                    "authors": paper["authors"] if "authors" in paper else "",
                    "doi": paper["doi"] if "doi" in paper else "",
                    "abstract": content,
                    "page": -1,
                },
            )
        ]

    ids = [get_id_for_a_page(paper_page) for paper_page in paper_pages]

    index_name = review_id_to_index(review_id)
    elastic_vector_search = ElasticsearchStore(
        es_connection=es_connection,
        index_name=index_name,
        embedding=embeddings,
    )
    elastic_vector_search.add_documents(paper_pages, ids=ids)


def remove_paper_from_elasticsearch_index(review_id, paper):
    logger.info("Removing paper from Elasticsearch index for RAG...")
    index_name = review_id_to_index(review_id)
    elastic_vector_search = ElasticsearchStore(
        es_connection=es_connection,
        index_name=index_name,
        embedding=embeddings,
    )

    page_number = -1

    first_page_id = get_id_for_a_page_by_metadata(
        paper["title"],
        page_number,
        paper["doi"],
    )

    try:
        logger.info(
            f"Removing page {page_number} with id {first_page_id} from index {index_name}"
        )
        elastic_vector_search.delete(ids=[first_page_id])
    except Exception:
        pass

    while True:
        page_number += 1
        page_id = get_id_for_a_page_by_metadata(
            paper["title"],
            page_number,
            paper["doi"],
        )
        try:
            if not elastic_vector_search.delete(ids=[page_id]):
                break
        except Exception:
            break
    logger.info(f"Finished removing pages from index {index_name}")


def clear_conversation(request, conversation_id: int):
    """
    Function to clear the conversation history.
    Args:
        screening (int): The screening ID associated with the conversation.
        conversation_id (int): The unique identifier for the conversation.
    Returns:
        str: Success message
    """

    if request.method != "PATCH":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        conversation = LLMConversation.objects.get(conversation_id=conversation_id)
    except LLMConversation.DoesNotExist:
        return JsonResponse(
            {
                "error": "Conversation not found",
            },
            status=404,
        )

    conversation.conversation = []
    conversation.save()

    return JsonResponse(
        {
            "message": "Conversation cleared",
        }
    )


def delete_conversation(request, conversation_id: int):
    """
    Function to delete the conversation.
    Args:
        screening (int): The screening ID associated with the conversation.
        conversation_id (int): The unique identifier for the conversation.
    Returns:
        str: Success message
    """

    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        conversation = LLMConversation.objects.get(conversation_id=conversation_id)
    except LLMConversation.DoesNotExist:
        return JsonResponse(
            {
                "error": "Conversation not found",
            },
            status=404,
        )

    conversation.delete()

    return JsonResponse(
        {
            "message": "Conversation deleted",
        }
    )


@login_required
def handle_conversation(request, conversation_id: int):
    """
    Function to handle the conversation.
    Args:
        screening (int): The screening ID associated with the conversation.
        conversation_id (int): The unique identifier for the conversation.
    Returns:
        str: Conversation history
    """

    if request.method == "PATCH":
        return clear_conversation(request, conversation_id)
    elif request.method == "DELETE":
        return delete_conversation(request, conversation_id)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


def get_conversation_ids(request, screening_id: int):
    """
    Function to get the conversation IDs.
    Args:
        screening (int): The screening ID associated with the conversation.
    Returns:
        str: Conversation IDs
    """

    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    review = LiteratureReview.objects.get(id=screening_id)
    if not review:
        return JsonResponse({"error": "Screening not found"}, status=404)

    if request.user not in review.members.all():
        return JsonResponse({"error": "User not in review"}, status=403)

    conversations = LLMConversation.objects.filter(screening_id=review).values_list(
        "conversation_id", flat=True
    )

    return JsonResponse(
        {
            "conversation_ids": list(conversations),
        }
    )


def add_conversation(request, screening_id: int):
    """
    Function to add a conversation to the database.
    Args:
        screening (int): The screening ID associated with the conversation.
    Returns:
        str: Conversation ID
    """

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    review = LiteratureReview.objects.get(id=screening_id)
    if not review:
        return JsonResponse({"error": "Screening not found"}, status=404)

    if request.user not in review.members.all():
        return JsonResponse({"error": "User not in review"}, status=403)

    new_conversation = LLMConversation.objects.create(screening_id=review)

    logger.info(new_conversation)

    return JsonResponse(
        {
            "conversation_id": new_conversation.conversation_id,
        }
    )


@login_required
def manage_conversations(request, screening_id: int):
    """
    Function to manage the conversation.
    Args:
        screening (int): The screening ID associated with the conversation.
    Returns:
        str: Conversation ID
    """

    if request.method == "POST":
        return add_conversation(request, screening_id)
    elif request.method == "GET":
        return get_conversation_ids(request, screening_id)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def ask_agent(request, conversation_id: int):
    """
    Function to ask the agent a question.
    Args:
        screening (int): The screening ID associated with the conversation.
        conversation_id (int): The unique identifier for the conversation.

    Body:
        {
            "question": "[Your question here]"
        }
    Returns:
        str: Answer from the agent
    """

    logger.info("Asking agent...")

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    logger.info("Correct method")

    try:
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    logger.info("JSON decoded")

    if "question" not in body:
        return JsonResponse({"error": "Missing question"}, status=400)

    question = body.get("question", None)

    if not question:
        return JsonResponse({"error": "Empty question"}, status=400)

    logger.info(f"Question received: {question}")

    try:
        conversation = LLMConversation.objects.get(conversation_id=conversation_id)
    except LLMConversation.DoesNotExist:
        return JsonResponse(
            {
                "error": "Conversation not found",
            },
            status=404,
        )
    except LLMConversation.MultipleObjectsReturned:
        raise ValueError("Multiple conversations found")

    logger.info("Conversation found")

    history = conversation.conversation

    system_prompt = """
    You are a helpful reasearch assistant. Your task is to help the user with their research concerning systematic review.
    The user have selected a set of research papers and you have access to them.
    You are given access to a database of research papers and a RAG system that can help you access the information about the selected papers.
    When you are asked a question, you should first check if the answer is in the database if this is a question that can be answered by the analysis of the papers.
    Every citation should be in the form of [1] or [2] or [3] etc. depending on the number of citations.
    At the end of the answer, you should provide a list of references in the form of [1] Paper title, authors, doi, page number, each one in a new line.
    If the question is not related to the papers, inform the user that the question is not related to the papers and you cannot help them with that.
    If you are unsure whether it is related to the papers, you should assume that it is.
    You should use tools rather too much than too little. You should try your best to answer the question using the tools.
    You can use the tools as many times as you want.
    You should always conform to the format required by the tools' input.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    chat_history = [(item.get("role"), item.get("content")) for item in history]

    review_id = conversation.screening_id.pk
    index_name = review_id_to_index(review_id)

    logger.info(f"Id: {review_id}")
    logger.info(f"Index name: {index_name}")

    elastic_vector_search = ElasticsearchStore(
        es_connection=es_connection,
        index_name=index_name,
        embedding=embeddings,
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-04-17",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=1,
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=elastic_vector_search.as_retriever(search_kwargs={"k": 3}),
    )

    @tool
    def rag_tool(query: str) -> str:
        """Use this tool to get information from the RAG model if needed.
        This tool allows you to ask questions about the papers selected by the user.
        This tool should return the answer with all the necessary citations.
        Sometimes the tool will not be able to answer the question, in that case, you should try to formulate the question in a different way.
        Most often than not, the problem with this tool's answer will be in your question formulation, so you should try to rephrase it them
        as this tool will try to answer your question very literally.
        """
        return rag_chain.invoke(query)

    @tool
    def elastic_search_tool(query: str) -> str:
        """Use this tool to get information from the Elasticsearch index if needed.
        This tool allows you to ask questions about the papers selected by the user.
        This tool should return the answer together with the metadata of the paper, by default returning the first 3 results.
        """
        results = elastic_vector_search.similarity_search(query, k=3)

        response = ""
        for i, result in enumerate(results):
            response += f"Result {i + 1}:\n"
            response += f"Title: {result.metadata['title']}\n"
            response += f"Authors: {result.metadata['authors']}\n"
            response += f"DOI: {result.metadata['doi']}\n"
            response += f"Page: {result.metadata['page']}\n\n"
            response += f"Content:\n{result.page_content}\n\n\n\n"

        return response

    tools = [rag_tool, elastic_search_tool]

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, max_iterations=15
    )
    result = agent_executor.invoke({"input": question, "chat_history": chat_history})[
        "output"
    ]

    logger.info(f"Result: {result}")

    conversation.conversation.extend(
        [
            {
                "role": "user",
                "content": question,
            },
            {
                "role": "assistant",
                "content": result,
            },
        ]
    )

    conversation.save()

    logger.info(result)
    return JsonResponse(
        {
            "answer": result,
        }
    )
