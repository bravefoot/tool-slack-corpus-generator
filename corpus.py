from cachier import cachier
from pathlib import Path
import slack
import json
from collections import Counter, defaultdict
import pandas as pd


slack_channel = "CUXD81R6X"
slack_token = ""  # REDACTED
api = slack.WebClient(slack_token)


def build_corpus(skills, introductions, channels):
    corpus, relations = {}, []  
    general_channels = set(['announcements', 'discussion-resources', 'questions-support-feedback', 'casual-discussion', 'introductions', 'media-published-articles'])
    channels = [c for c in channels if len(c['members']) > 10 and c['name'] not in general_channels]

    for user, introduction in introductions.items():
        relations += [[introduction.casefold(), [
            channel["name"] for channel in channels
            if user in channel["members"]
            ]]]

    for introduction, channels in relations:
        for channel in channels:
            if not corpus.get(channel):
                corpus[channel] = {}
            for token in tokenize(skills, introduction):
                corpus[channel][token] = corpus[channel].get(token, 0) + 1
    
    df = pd.DataFrame(corpus)
    row_maxes = df.max(axis=1)
    normal_row = df.T.divide(row_maxes).T
    col_maxes = normal_row.max()
    final_df = normal_row.divide(col_maxes)

    channel_keywords = defaultdict(set)
    for row in final_df.iterrows():
        keyword_info = row[1].nlargest(4)
        keyword = keyword_info.name
        keyword_channels = keyword_info.index.to_list()
        for channel in keyword_channels:
            channel_keywords[channel].add(keyword)
    channel_keywords = {c:list(k) for c,k in channel_keywords.items()}
    return channel_keywords


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
    with open(Path(__file__).parent / "output" / "corpus.json", "w") as corpus_file:
        corpus = build_corpus(
            skill_file.read().split("\n"),
            fetch_introductions(slack_channel),
            fetch_channels()
            )
        json.dump(corpus, corpus_file)
