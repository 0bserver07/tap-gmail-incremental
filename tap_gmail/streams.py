"""Stream type classes for tap-gmail."""

from pathlib import Path
from typing import Any, Dict, Optional, Iterable
import requests

from singer_sdk.helpers.jsonpath import extract_jsonpath
from tap_gmail.client import GmailStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


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
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        data = response.json()
        
        # Handle response from history endpoint differently from messages endpoint
        if "history" in data:
            seen_ids = set()
            for history in data.get("history", []):
                # Extract message IDs from all relevant history records
                for msg_type in ["messagesAdded", "messagesChanged", "labelsAdded", "labelsRemoved"]:
                    for msg in history.get(msg_type, []):
                        if "message" in msg and msg["message"]["id"] not in seen_ids:
                            seen_ids.add(msg["message"]["id"])
                            yield {
                                "id": msg["message"]["id"],
                                "threadId": msg["message"].get("threadId", ""),
                                "historyId": history.get("id")
                            }
        else:
            # Default behavior for regular messages endpoint
            for item in extract_jsonpath(self.records_jsonpath, input=data):
                # Add historyId if it's in the response metadata
                if "historyId" in data:
                    item["historyId"] = data["historyId"]
                yield item


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
