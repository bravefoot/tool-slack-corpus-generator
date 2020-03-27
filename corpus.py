from cachier import cachier
from pathlib import Path
import slack
import json


slack_channel = "CUXD81R6X"
slack_token = ""  # REDACTED
api = slack.WebClient(slack_token)


def build_corpus(skills, introductions, channels):
    corpus, relations = {}, []

    for user, introduction in introductions.items():
        relations += [[introduction.casefold(), [
            channel["name"] for channel in channels
            if user in channel["members"]
            ]]]

    for introduction, channels in relations:
        for channel in channels:
            if not corpus.get(channel):
                corpus[channel] = set()
            for token in tokenize(skills, introduction):
                corpus[channel].add(token)

    for channel, skills in corpus.items():
        corpus[channel] = list(filter(None, skills))

    return corpus


def tokenize(skills, text):
    return [skill for skill in skills if skill in text]


@cachier(cache_dir=Path(__file__).parent / "cache")
def fetch_introductions(channel):
    return {
        message["user"]: message["text"]
        for page in api.conversations_history(channel=channel)
        for message in page["messages"]
        if message["type"] == "message" and "thread_ts" not in message
        }


@cachier(cache_dir=Path(__file__).parent / "cache")
def fetch_channels():
    return [{
            "name": channel["name"],
            "identifier": channel["id"],
            "topic": channel["topic"]["value"],
            "purpose": channel["purpose"]["value"],
            "members": list(fetch_members(channel["id"]))
            }
        for channel in api.conversations_list()["channels"]
        if not channel["is_archived"]
        ]


@cachier(cache_dir=Path(__file__).parent / "cache")
def fetch_members(channel):
    return [
        member
        for page in api.conversations_members(channel=channel)
        for member in page["members"][:10]
        ]


with open(Path(__file__).parent / "input" / "skills.txt", "r") as skill_file:
    with open(Path(__file__).parent / "output" / corpus.json", "w") as corpus_file:
        corpus = build_corpus(
            skill_file.read().split("\n"),
            fetch_introductions(slack_channel),
            fetch_channels()
            )
        json.dump(corpus, corpus_file)
