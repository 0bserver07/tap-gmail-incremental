"""Stream type classes for tap-gmail."""

from pathlib import Path
from typing import Any, Dict, Optional, Iterable
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from singer_sdk.helpers.jsonpath import extract_jsonpath
from tap_gmail.client import GmailStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
BATCH_SIZE = 50  # Gmail API batch size limit

class MessageListStream(GmailStream):
    """Define custom stream."""

    name = "message_list"
    primary_keys = ["id"]
    # Add replication key for incremental fetching
    replication_key = "historyId"
    schema_filepath = SCHEMAS_DIR / "message_list.json"
    records_jsonpath = "$.messages[*]"
    next_page_token_jsonpath = "$.nextPageToken"

    @property
    def path(self):
        """Set the path for the stream."""
        # When using incremental with a historyId, we'll override this in get_url_params
        return "/gmail/v1/users/" + self.config["user_id"] + "/messages"

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {"message_id": record["id"]}

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = super().get_url_params(context, next_page_token)
        params["includeSpamTrash"]=self.config["messages.include_spam_trash"]
        params["q"]=self.config.get("messages.q")

        # Add historyId for incremental fetching if available and enabled
        if self.config.get("use_incremental", False) and self.get_starting_replication_key_value(context):
            # Switch to the history endpoint for incremental fetching
            self._path = "/gmail/v1/users/" + self.config["user_id"] + "/history"
            params["startHistoryId"] = self.get_starting_replication_key_value(context)
            params["historyTypes"] = "messageAdded,messageChanged,labelAdded,labelRemoved"

        return params

    def _batch_get_messages(self, message_ids: list) -> list:
        """Get messages in batch to reduce API calls."""
        if not message_ids:
            return []

        # Create Gmail API service
        credentials = Credentials(
            None,
            refresh_token=self.config["oauth_credentials"]["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.config["oauth_credentials"]["client_id"],
            client_secret=self.config["oauth_credentials"]["client_secret"],
        )
        service = build('gmail', 'v1', credentials=credentials)

        # Split into batches of BATCH_SIZE
        batches = [message_ids[i:i + BATCH_SIZE] for i in range(0, len(message_ids), BATCH_SIZE)]
        messages = []

        for batch in batches:
            try:
                # Use messages.batchGet for efficiency
                batch_request = service.users().messages().batchGet(
                    userId=self.config["user_id"],
                    ids=batch
                ).execute()
                messages.extend(batch_request.get('messages', []))
            except Exception as e:
                self.logger.error(f"Error fetching batch of messages: {str(e)}")
                # Fall back to individual fetches if batch fails
                for msg_id in batch:
                    try:
                        msg = service.users().messages().get(
                            userId=self.config["user_id"],
                            id=msg_id
                        ).execute()
                        messages.append(msg)
                    except Exception as e:
                        self.logger.error(f"Error fetching message {msg_id}: {str(e)}")

        return messages

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        data = response.json()

        # Handle response from history endpoint differently from messages endpoint
        if "history" in data:
            seen_ids = set()
            message_ids = []

            # Extract message IDs from history items
            for history_item in data.get("history", []):
                # Get messages from all relevant history types
                for msg_type in ["messages", "added", "messages", "messagesAdded"]:
                    for msg in history_item.get(msg_type, []):
                        if msg.get("id") not in seen_ids:
                            message_ids.append(msg.get("id"))
                            seen_ids.add(msg.get("id"))

            # Batch fetch the actual messages
            messages = self._batch_get_messages(message_ids)
            for msg in messages:
                if msg:
                    msg["historyId"] = history_item.get("id")  # Add historyId to message
                    yield msg
        else:
            # For regular message list endpoint
            message_ids = [msg.get("id") for msg in extract_jsonpath(self.records_jsonpath, data)]
            messages = self._batch_get_messages(message_ids)
            yield from (msg for msg in messages if msg)


class MessagesStream(GmailStream):

    name = "messages"
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "messages.json"
    parent_stream_type = MessageListStream
    ignore_parent_replication_keys = True
    state_partitioning_keys = []

    @property
    def path(self):
        """Set the path for the stream."""
        return "/gmail/v1/users/" + self.config["user_id"] + "/messages/{message_id}"
