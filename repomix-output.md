This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded

## Additional Info

# Directory Structure
```
.github/
  workflows/
    ci_workflow.yml
    project_add.yml
    release_workflow.yml
.secrets/
  .gitignore
tap_gmail/
  schemas/
    message_list.json
    messages.json
  tests/
    __init__.py
    test_core.py
  auth.py
  client.py
  streams.py
  tap.py
.gitignore
generate_refresh_token.py
LICENSE
meltano.yml
mypy.ini
pyproject.toml
README.md
tox.ini
```

# Files

## File: .github/workflows/ci_workflow.yml
````yaml
### A CI workflow template that runs linting and python testing
### TODO: Modify as needed or as desired.

name: Test tap-gmail

on: [push]

jobs:
  linting:

    runs-on: ubuntu-latest
    strategy:
      matrix:
        # Only lint using the primary version used for dev
        python-version: ["3.10"]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: 1.4.2
    - name: Install dependencies
      run: |
        poetry install
    - name: Run lint command from tox.ini
      run: |
        poetry run tox -e lint

  # pytest:

  #   runs-on: ubuntu-latest
  #   env:
  #     GITHUB_TOKEN: ${{secrets.GITHUB_TOKEN}}
  #   strategy:
  #     matrix:
  #       python-version: ["3.7", "3.8", "3.9", "3.10", "3.11"]

  #   steps:
  #   - uses: actions/checkout@v2
  #   - name: Set up Python ${{ matrix.python-version }}
  #     uses: actions/setup-python@v2
  #     with:
  #       python-version: ${{ matrix.python-version }}
  #   - name: Install Poetry
  #     uses: snok/install-poetry@v1
  #     with:
  #       version: 1.4.2
  #   - name: Install dependencies
  #     run: |
  #       poetry install
  #   - name: Test with pytest
  #     run: |
  #       poetry run pytest --capture=no
````

## File: .github/workflows/project_add.yml
````yaml
# Managed by Pulumi. Any edits to this file will be overwritten.

name: Add issues and PRs to MeltanoLabs Overview Project

on:
  issues:
    types:
      - opened
      - reopened
      - transferred
  pull_request:
    types:
      - opened
      - reopened

jobs:
  add-to-project:
    name: Add issue to project
    runs-on: ubuntu-latest
    if: ${{ github.actor != 'dependabot[bot]' }}
    steps:
      - uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/orgs/MeltanoLabs/projects/3
          github-token: ${{ secrets.MELTYBOT_PROJECT_ADD_PAT }}
````

## File: .github/workflows/release_workflow.yml
````yaml
name: Upload Python Package

on:
  release:
    types: [published]  # Trigger only when a release is published, not when a release is drafted

permissions:
  contents: write  # Needed to upload artifacts to the release
  id-token: write  # Needed for OIDC PyPI publishing

jobs:
  build_deploy:

    runs-on: ubuntu-latest
    environment: publishing

    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
    - name: Build package
      run: |
        poetry self add "poetry-dynamic-versioning[plugin]"
        poetry config repositories.testpypi https://test.pypi.org/legacy/
        poetry dynamic-versioning --no-cache
        poetry build
    - name: Upload wheel to release
      uses: svenstaro/upload-release-action@v2
      with:
        repo_token: ${{ secrets.GITHUB_TOKEN }}
        file: dist/*.whl
        tag: ${{ github.ref }}
        overwrite: true
        file_glob: true
    - name: Publish
      uses: pypa/gh-action-pypi-publish@v1.8.5
````

## File: .secrets/.gitignore
````
# IMPORTANT! This folder is hidden from git - if you need to store config files or other secrets,
# make sure those are never staged for commit into your git repo. You can store them here or another
# secure location.
#
# Note: This may be redundant with the global .gitignore for, and is provided
# for redundancy. If the `.secrets` folder is not needed, you may delete it
# from the project.

*
!.gitignore
````

## File: tap_gmail/schemas/message_list.json
````json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "The immutable ID of the message."
    },
    "threadId": {
      "type": "string",
      "description": "The ID of the thread the message belongs to."
    },
    "historyId": {
      "type": "string",
      "description": "The ID of the last history record that modified this message."
    }
  }
}
````

## File: tap_gmail/schemas/messages.json
````json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "The immutable ID of the message."
    },
    "threadId": {
      "type": "string",
      "description": "The ID of the thread the message belongs to."
    },
    "labelIds": {
      "description": "List of IDs of labels applied to this message.",
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "snippet": {
      "type": "string",
      "description": "A short part of the message text."
    },
    "historyId": {
      "type": "string",
      "description": "The ID of the last history record that modified this message."
    },
    "internalDate": {
      "type": "string",
      "description": "The internal message creation timestamp (epoch ms), which determines ordering in the inbox. For normal SMTP-received email, this represents the time the message was originally accepted by Google, which is more reliable than the Date header. However, for API-migrated mail, it can be configured by client to be based on the Date header."
    },
    "payload": { "$ref": "#/definitions/message_part" },
    "sizeEstimate": {
      "type": "integer",
      "description": "Estimated size in bytes of the message."
    },
    "raw": {
      "type": "string",
      "description": "The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in messages.get and drafts.get responses when the format=RAW parameter is supplied. A base64-encoded string."
    }
  },
  "definitions": {
    "header": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "The name of the header before the : separator. For example, To."
        },
        "value": {
          "type": "string",
          "description": "The value of the header after the : separator. For example, someuser@example.com."
        }
      }
    },
    "message_part_body": {
      "type": "object",
      "properties": {
        "attachmentId": {
          "type": "string",
          "description": "When present, contains the ID of an external attachment that can be retrieved in a separate messages.attachments.get request. When not present, the entire content of the message part body is contained in the data field."
        },
        "size": {
          "type": "integer",
          "description": "Number of bytes for the message part data (encoding notwithstanding)."
        },
        "data": {
          "type": "string",
          "description": "The body data of a MIME message part as a base64url encoded string. May be empty for MIME container types that have no message body or when the body data is sent as a separate attachment. An attachment ID is present if the body data is contained in a separate attachment. A base64-encoded string."
        }
      },
      "description": "The message part body for this part, which may be empty for container MIME message parts."
    },
    "message_part": {
      "type": "object",
      "properties": {
        "partId": {
          "type": "string",
          "description": "The immutable ID of the message part."
        },
        "mimeType": {
          "type": "string",
          "description": "The MIME type of the message part."
        },
        "filename": {
          "type": "string",
          "description": "The filename of the attachment. Only present if this message part represents an attachment."
        },
        "headers": {
          "type": "array",
          "items": { "$ref": "#/definitions/header" },
          "description": "List of headers on this message part. For the top-level message part, representing the entire message payload, it will contain the standard RFC 2822 email headers such as To, From, and Subject."
        },
        "body": { "$ref": "#/definitions/message_part_body" },
        "parts": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/message_part"
          }
        }
      },
      "description": "A single MIME message part."
    }
  }
}
````

## File: tap_gmail/tests/__init__.py
````python
"""Test suite for tap-gmail."""
````

## File: tap_gmail/tests/test_core.py
````python
"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_standard_tap_tests

from tap_gmail.tap import TapGmail

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    # TODO: Initialize minimal tap config
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(
        TapGmail,
        config=SAMPLE_CONFIG
    )
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.
````

## File: tap_gmail/auth.py
````python
"""Gmail Authentication."""


from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behaviour interferes with your use-case, you can remove the metaclass.
class GmailAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for Gmail."""

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the Gmail API."""
        oauth_credentials = self.config.get("oauth_credentials", {})
        return {
            "grant_type": "refresh_token",
            "client_id": oauth_credentials.get("client_id"),
            "client_secret": oauth_credentials.get("client_secret"),
            "refresh_token": oauth_credentials.get("refresh_token"),
        }

    @classmethod
    def create_for_stream(cls, stream) -> "GmailAuthenticator":
        return cls(
            stream=stream,
            auth_endpoint="https://oauth2.googleapis.com/token",
            oauth_scopes="https://www.googleapis.com/auth/gmail.readonly",
        )
````

## File: tap_gmail/client.py
````python
"""REST client handling, including GmailStream base class."""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

import requests
from memoization import cached
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_gmail.auth import GmailAuthenticator

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class GmailStream(RESTStream):
    """Gmail stream class."""

    url_base = "https://gmail.googleapis.com"

    @property
    @cached
    def authenticator(self) -> GmailAuthenticator:
        """Return a new authenticator object."""
        return GmailAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        if self.next_page_token_jsonpath:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            first_match = next(iter(all_matches), None)
            next_page_token = first_match
        else:
            next_page_token = None

        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["pageToken"] = next_page_token
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    def get_starting_replication_key_value(self, context: Optional[dict]) -> Optional[Any]:
        """Get the starting value for the replication key from state or config."""
        rep_key = self.get_replication_key()
        if not rep_key:
            return None

        state_value = self.get_context_state(context).get(rep_key) if self.is_state_persistent else None

        # If no state exists but an initial history ID is provided in config, use that
        if state_value is None and rep_key == "historyId" and "initial_history_id" in self.config:
            return self.config["initial_history_id"]

        return state_value
````

## File: tap_gmail/streams.py
````python
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
        if self.config.get("messages.q"):
            params["q"]=self.config.get("messages.q")

        # Add historyId for incremental fetching if available and enabled
        use_incremental = self.config.get("use_incremental", False)
        history_id = self.get_starting_replication_key_value(context)

        if use_incremental and history_id:
            self.logger.info(f"Using incremental sync with history API. Starting from historyId: {history_id}")
            # Switch to the history endpoint for incremental fetching
            self._path = "/gmail/v1/users/" + self.config["user_id"] + "/history"
            params["startHistoryId"] = history_id
            params["historyTypes"] = "messageAdded,messageChanged,labelAdded,labelRemoved"
        else:
            self.logger.info("Using standard message list endpoint (not incremental or no historyId)")
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
````

## File: tap_gmail/tap.py
````python
"""Gmail tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_gmail.streams import GmailStream, MessageListStream, MessagesStream

STREAM_TYPES = [MessageListStream, MessagesStream]


class TapGmail(Tap):
    """Gmail tap class."""

    name = "tap-gmail"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "oauth_credentials.client_id",
            th.StringType,
            description="Your google client_id",
        ),
        th.Property(
            "oauth_credentials.client_secret",
            th.StringType,
            description="Your google client_secret",
        ),
        th.Property(
            "oauth_credentials.refresh_token",
            th.StringType,
            description="Your google refresh token",
        ),
        th.Property(
            "messages.q",
            th.StringType,
            description="Only return messages matching the specified query. Supports the same query format as the Gmail search box. For example, \"from:someuser@example.com rfc822msgid:<somemsgid@example.com> is:unread\". Parameter cannot be used when accessing the api using the gmail.metadata scope. https://developers.google.com/gmail/api/reference/rest/v1/users.messages/list#query-parameters",
        ),
        th.Property("user_id", th.StringType, description="Your Gmail User ID"),
        th.Property(
            "messages.include_spam_trash",
            th.BooleanType,
            description="Include messages from SPAM and TRASH in the results.",
            default=False,
        ),
        # Add new configuration options for incremental fetching
        th.Property(
            "use_incremental",
            th.BooleanType,
            description="Enable incremental fetching using Gmail history API",
            default=True,
        ),
        th.Property(
            "initial_history_id",
            th.StringType,
            description="Initial history ID to start fetching from if no state exists",
            required=False,
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
````

## File: .gitignore
````
# Secrets and internal config files
**/.secrets/*
.env

# Ignore meltano internal cache and sqlite systemdb
.meltano/
plugins/
output/

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/
````

## File: generate_refresh_token.py
````python
#!/usr/bin/env python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified from: https://github.com/googleads/googleads-python-lib/blob/master/examples/adwords/authentication/generate_refresh_token.py

"""Generates refresh token for Gmail using the Installed Application flow."""

import argparse
import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

# Your OAuth2 Client ID and Secret. If you do not have an ID and Secret yet,
# please go to https://console.developers.google.com and create a set.
DEFAULT_CLIENT_ID = None
DEFAULT_CLIENT_SECRET = None

# The Gmail API OAuth2 scope.
SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
# The redirect URI set for the given Client ID. The redirect URI for Client ID
# generated for an installed application will always have this value.
_REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"

parser = argparse.ArgumentParser(
    description="Generates a refresh token with " "the provided credentials."
)
parser.add_argument(
    "--client_id",
    default=DEFAULT_CLIENT_ID,
    help="Client Id retrieved from the Developer's Console.",
)
parser.add_argument(
    "--client_secret",
    default=DEFAULT_CLIENT_SECRET,
    help="Client Secret retrieved from the Developer's " "Console.",
)
parser.add_argument(
    "--additional_scopes",
    default=None,
    help="Additional scopes to apply when generating the "
    "refresh token. Each scope should be separated by a comma.",
)


class ClientConfigBuilder(object):
    """Helper class used to build a client config dict used in the OAuth 2.0 flow."""

    _DEFAULT_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
    _DEFAULT_TOKEN_URI = "https://accounts.google.com/o/oauth2/token"
    CLIENT_TYPE_WEB = "web"
    CLIENT_TYPE_INSTALLED_APP = "installed"

    def __init__(
        self,
        client_type=None,
        client_id=None,
        client_secret=None,
        auth_uri=_DEFAULT_AUTH_URI,
        token_uri=_DEFAULT_TOKEN_URI,
    ):
        self.client_type = client_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_uri = auth_uri
        self.token_uri = token_uri

    def Build(self):
        """Builds a client config dictionary used in the OAuth 2.0 flow."""
        if all(
            (
                self.client_type,
                self.client_id,
                self.client_secret,
                self.auth_uri,
                self.token_uri,
            )
        ):
            client_config = {
                self.client_type: {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": self.auth_uri,
                    "token_uri": self.token_uri,
                }
            }
        else:
            raise ValueError("Required field is missing.")

        return client_config


def main(client_id, client_secret, scopes):
    """Retrieve and display the access and refresh token."""
    client_config = ClientConfigBuilder(
        client_type=ClientConfigBuilder.CLIENT_TYPE_WEB,
        client_id=client_id,
        client_secret=client_secret,
    )

    flow = InstalledAppFlow.from_client_config(client_config.Build(), scopes=scopes)
    # Note that from_client_config will not produce a flow with the
    # redirect_uris (if any) set in the client_config. This must be set
    # separately.
    flow.redirect_uri = _REDIRECT_URI

    auth_url, _ = flow.authorization_url(prompt="consent")

    print(
        "Log into the Google Account you use to access your Gmail account "
        "and go to the following URL: \n%s\n" % auth_url
    )
    print("After approving the token enter the verification code (if specified).")
    code = input("Code: ").strip()

    try:
        flow.fetch_token(code=code)
    except InvalidGrantError as ex:
        print("Authentication has failed: %s" % ex)
        sys.exit(1)

    print("Access token: %s" % flow.credentials.token)
    print("Refresh token: %s" % flow.credentials.refresh_token)


if __name__ == "__main__":
    args = parser.parse_args()
    configured_scopes = [SCOPE]
    if not (
        any([args.client_id, DEFAULT_CLIENT_ID])
        and any([args.client_secret, DEFAULT_CLIENT_SECRET])
    ):
        raise AttributeError("No client_id or client_secret specified.")
    if args.additional_scopes:
        configured_scopes.extend(args.additional_scopes.replace(" ", "").split(","))
    main(args.client_id, args.client_secret, configured_scopes)
````

## File: LICENSE
````
MIT License

Copyright (c) 2022 Ken Payne

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

## File: meltano.yml
````yaml
version: 1
send_anonymous_usage_stats: true
project_id: tap-gmail
plugins:
  extractors:
  - name: tap-gmail
    namespace: tap_gmail
    pip_url: -e .
    capabilities:
    - state
    - catalog
    - discover
    settings:
    - name: oauth_credentials.client_id
    - name: oauth_credentials.client_secret
    - name: oauth_credentials.refresh_token
    - name: user_id
    select:
    - messages.*
  loaders:
  - name: target-jsonl
    variant: andyh1203
    pip_url: target-jsonl
````

## File: mypy.ini
````
[mypy]
python_version = 3.9
warn_unused_configs = True

[mypy-backoff.*]
ignore_missing_imports = True
````

## File: pyproject.toml
````toml
[tool.poetry]
name = "meltanolabs-tap-gmail"
version = "0.0.0"
description = "`tap-gmail` is a Singer tap for Gmail, built with the Meltano SDK for Singer Taps."
readme = "README.md"
authors = ["Ken Payne"]
keywords = [
    "ELT",
    "Gmail",
]
license = "Apache 2.0"
packages = [
    { include = "tap_gmail" },
]


[tool.poetry.dependencies]
python = "<3.12,>=3.7.1"
requests = "^2.25.1"
singer-sdk = "^0.24.0"

[tool.poetry.dev-dependencies]
pytest = "^6.2.5"
tox = "^3.24.4"
flake8 = "^3.9.2"
black = "^21.9b0"
pydocstyle = "^6.1.1"
mypy = "^0.910"
types-requests = "^2.26.1"
isort = "^5.10.1"

[tool.isort]
profile = "black"
multi_line_output = 3 # Vertical Hanging Indent
src_paths = "tap_gmail"

[build-system]
requires = ["poetry-core>=1.0.8", "poetry-dynamic-versioning"]
build-backend = "poetry_dynamic_versioning.backend"

[tool.poetry.scripts]
# CLI declaration
tap-gmail = 'tap_gmail.tap:TapGmail.cli'

[tool.poetry-dynamic-versioning]
enable = true
vcs = "git"
style = "semver"
````

## File: README.md
````markdown
# tap-gmail

`tap-gmail` is a Singer tap for Gmail.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

```bash
pipx install tap-gmail
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-gmail --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

## Usage

You can easily run `tap-gmail` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-gmail --version
tap-gmail --help
tap-gmail --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_gmail/tests` subfolder and
then run:

```bash
poetry run pytest
```

You can also test the `tap-gmail` CLI interface directly using `poetry run`:

```bash
poetry run tap-gmail --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-gmail
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-gmail --version
# OR run a test `elt` pipeline:
meltano elt tap-gmail target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
````

## File: tox.ini
````
# This file can be used to customize tox tests as well as other test frameworks like flake8 and mypy

[tox]
envlist = py38
; envlist = py37, py38, py39
isolated_build = true

[testenv]
whitelist_externals = poetry

commands =
    poetry install -v
    poetry run pytest
    poetry run black --check tap_gmail/
    poetry run flake8 tap_gmail
    poetry run pydocstyle tap_gmail
    poetry run mypy tap_gmail --exclude='tap_gmail/tests'

[testenv:pytest]
# Run the python tests.
# To execute, run `tox -e pytest`
envlist = py37, py38, py39
commands =
    poetry install -v
    poetry run pytest

[testenv:format]
# Attempt to auto-resolve lint errors before they are raised.
# To execute, run `tox -e format`
commands =
    poetry install -v
    poetry run black tap_gmail/
    poetry run isort tap_gmail

[testenv:lint]
# Raise an error if lint and style standards are not met.
# To execute, run `tox -e lint`
commands =
    poetry install -v
    poetry run black --check --diff tap_gmail/
    poetry run isort --check tap_gmail
    poetry run flake8 tap_gmail
    poetry run pydocstyle tap_gmail
    # refer to mypy.ini for specific settings
    poetry run mypy tap_gmail --exclude='tap_gmail/tests'

[flake8]
ignore = W503
max-line-length = 88
max-complexity = 10

[pydocstyle]
ignore = D105,D203,D213
````
