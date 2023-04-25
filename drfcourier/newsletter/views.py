import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .db import subscribers_collection
import json
from bson.json_util import dumps, loads


NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = "2eb91792d1e2444e9db08ad4e5b79e10"

NOTION_BASE_URL = "https://api.notion.com/v1"

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def format_newsletter_data(data):
    props = data['properties']
    return dict({
        "title": props["title"]['title'][0]['text']['content'],
        "status": props['status']['select']['name'],
        "published_at": props['publish date']['date']['start'],
        "id": data['id']
    })


def get_newsletters(raw_data):
    newsletters = raw_data["results"]
    return map(format_newsletter_data, newsletters)


class Newsletters(APIView):
    def get(self, request):
        res = requests.post(
            f"{NOTION_BASE_URL}/databases/{DATABASE_ID}/query", headers=headers)

        newsletters = get_newsletters(res.json())
        return Response(data={"newsletters": newsletters})


def get_page_detail(properties):
    block_types_map_to_html_tag = {
        "heading_1": {"tag": "h1", "content": "heading_1"},
        "heading_2": {"tag": "h2", "content": "heading_2"},
        "heading_3": {"tag": "h3", "content": "heading_3"},
        "heading_3": {"tag": "h3", "content": "heading_3"},
        "paragraph": {"tag": "p", "content": "paragraph"}
    }
    blocks = properties['results']

    def mapper(block):
        block_type = block["type"]
        tag = block_types_map_to_html_tag[block_type]["tag"]
        rich_text = block[block_types_map_to_html_tag[block_type]
                          ["content"]]["rich_text"]

        if len(rich_text) <= 0:
            return None

        content = rich_text[0]["plain_text"]

        return f"<{tag}>{content}</{tag}>"

    return filter(lambda x: x != None, map(mapper, blocks))


class NewsletterDetail(APIView):
    def get(self, request, *args, **kwargs):
        id = kwargs['newsletter_id']
        res = requests.get(
            f"{NOTION_BASE_URL}/blocks/{id}/children", headers=headers)
        newsletter_data = get_page_detail(res.json())

        return Response(data={"newsletter": newsletter_data})


class Subscription(APIView):
    def get(self, request):
        subscribers = subscribers_collection.find()
        return Response(data={"subscribers": json.loads(dumps(subscribers))})

    def post(self, request):
        subscriber_data = json.loads(request.body)
        if subscribers_collection.find_one({"email": subscriber_data['email']}):
            return Response(data={"message": "Bad Request! User already exist!"}, status=400)

        user_id = subscribers_collection.insert_one(
            subscriber_data).inserted_id
        return Response(data={"subscriber_id": str(user_id)})
