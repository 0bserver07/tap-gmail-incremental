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
        params["includeSpamTrash"] = self.config["messages.include_spam_trash"]
        if self.config.get("messages.q"):
            params["q"] = self.config.get("messages.q")

        # Use incremental fetching exclusively based on history API when enabled
        if self.config.get("use_incremental", False):
            history_id = self.get_starting_replication_key_value(context)
            if not history_id:
                self.logger.error("Incremental sync is enabled but no historyId is provided. Please set 'initial_history_id' in your config.")
                # Optionally, you can raise an exception here if desired:
                # raise ValueError("Missing initial_history_id for incremental sync.")
            self.logger.info(f"Using incremental sync with history API. Starting from historyId: {history_id}")
            self._path = "/gmail/v1/users/" + self.config["user_id"] + "/history"
            params["startHistoryId"] = history_id
            params["historyTypes"] = "messageAdded,messageChanged,labelAdded,labelRemoved"
        else:
            self.logger.info("Using standard message list endpoint (not incremental)")
            self._path = "/gmail/v1/users/" + self.config["user_id"] + "/messages"

            # Check if we have a timestamp filter to apply
            if self.config.get("messages.after_timestamp"):
                timestamp = self.config.get("messages.after_timestamp")
                self.logger.info(f"Filtering messages after timestamp: {timestamp}")
                # Add timestamp filter to the query
                timestamp_query = f"after:{int(timestamp)//1000}"
                if params.get("q"):
                    params["q"] = f"{params['q']} {timestamp_query}"
                else:
                    params["q"] = timestamp_query

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
        self.logger.info(f"Response data type: {'history API' if 'history' in data else 'message list'}")

        if "history" in data:
            # 1. Create message-to-history mapping FIRST
            message_history_map = {}
            message_ids = []
            latest_history_id = None

            for history_item in data.get("history", []):
                history_id = history_item.get("id")
                if history_id and (latest_history_id is None or int(history_id) > int(latest_history_id)):
                    latest_history_id = history_id

                # Look for messages in messagesAdded
                for msg in history_item.get("messagesAdded", []):
                    if "message" in msg:
                        msg_id = msg["message"]["id"]
                        message_history_map[msg_id] = history_id
                        message_ids.append(msg_id)

            # Update state with latest history ID if available
            if latest_history_id:
                self.logger.info(f"Updating state with latest historyId: {latest_history_id}")
                self.state = {self.replication_key: latest_history_id}

            # 2. Batch fetch ONLY after we have ALL mappings
            if message_ids:
                self.logger.info(f"Found {len(message_ids)} messages in history API response")
                messages = self._batch_get_messages(message_ids)
                # 3. Attach CORRECT history ID to EACH message
                for msg in messages:
                    if msg and msg.get("id") in message_history_map:
                        msg["historyId"] = message_history_map[msg.get("id")]
                        yield msg
            else:
                self.logger.info("No messages found in history API response")
        else:
            # Regular message list endpoint
            message_ids = [msg.get("id") for msg in extract_jsonpath(self.records_jsonpath, data)]
            if message_ids:
                self.logger.info(f"Found {len(message_ids)} messages in message list response")
                messages = self._batch_get_messages(message_ids)

                # Track the latest historyId to update state
                latest_history_id = None

                for msg in messages:
                    if msg:
                        # Add historyId from response data if available
                        if "historyId" in data:
                            msg["historyId"] = data["historyId"]

                        # Track the largest historyId we've seen
                        if msg.get("historyId") and (
                            latest_history_id is None or
                            int(msg["historyId"]) > int(latest_history_id)
                        ):
                            latest_history_id = msg["historyId"]

                        yield msg

                # Update state with latest history ID if available
                if latest_history_id:
                    self.logger.info(f"Updating state with latest historyId: {latest_history_id}")
                    self.state = {self.replication_key: latest_history_id}


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
