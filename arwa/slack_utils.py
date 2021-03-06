from typing import Dict, Iterator, List

from pydash import py_

import slack
from arwa.types import SlackUser


def list_users(client: slack.WebClient) -> List[SlackUser]:
    """
    List workspace users except bots and deactivated accounts.
    """

    response = client.users_list()
    members = response["members"]

    users = []
    for member in members:
        if member["is_bot"]:
            continue
        if member["deleted"]:
            continue
        if member["id"] == "USLACKBOT":
            continue
        users.append(SlackUser(member["id"], member["real_name"]))
    return users


def channel_name_to_id(name: str, client: slack.WebClient) -> str:
    """
    Return slack id for given channel name. This only works for the channel the
    slack client is part of.
    """

    response = client.users_conversations(types="public_channel,private_channel,mpim,im", exclude_archived=True)
    channels = response["channels"]

    result = py_.find(channels, lambda ch: ch.get("name", "") == name)

    if result:
        return result["id"]
    else:
        raise ValueError(f"Channel {name} not found")


def get_message_batches(conversation_id: str, client: slack.WebClient) -> Iterator[List[Dict]]:
    """
    Get messages in batches of requests.
    """

    response = client.conversations_history(channel=conversation_id)
    message_batch = response["messages"]

    if not message_batch:
        return

    yield message_batch

    while response["has_more"]:
        next_cursor = response["response_metadata"]["next_cursor"]
        response = client.conversations_history(channel=conversation_id, cursor=next_cursor)
        yield response["messages"]
