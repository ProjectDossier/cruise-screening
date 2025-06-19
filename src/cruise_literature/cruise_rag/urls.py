from django.urls import path
from .views import ask_agent, handle_conversation, manage_conversations

app_name = "cruise_rag"
urlpatterns = [
    path("ask/<int:conversation_id>/", ask_agent, name="ask_agent"),
    path(
        "conversation/<int:conversation_id>/",
        handle_conversation,
        name="handle_conversation",
    ),
    path(
        "conversations-manager/<int:screening_id>/",
        manage_conversations,
        name="manage_conversations",
    ),
]
