#!/usr/bin/env python3

"""
Github Notification RSS Feed
"""

from feedgen.feed import FeedGenerator
from requests.auth import HTTPBasicAuth
import requests

from flask import Flask, Response, send_file

app = Flask(__name__)

@app.route("/<username>/<token>/.atom", methods=["GET"])
def api_rss(username: str, token: str):
    """
    Get the rss feed for a user/token combo
    """
    auth = HTTPBasicAuth(username, token)
    endpoint = "https://api.github.com/notifications?all=true"

    req = requests.get(endpoint, auth=auth)
    if req.status_code != 200:
        # Report error back to client
        return req.text, req.status_code

    feed = FeedGenerator()
    feed.id("https://github.com/notifications")
    feed.title("Github Notifications")
    feed.language("en")

    for entry in req.json():
        url = entry["subject"]["url"]
        content = requests.get(url)
        if content.status_code == 200:
            url = content.json()["html_url"]

        fentry = feed.add_entry(order="append")
        fentry.id(entry["url"])
        fentry.title(f"[{entry['subject']['type']}] {entry['subject']['title']}")
        fentry.link(href=url)
        fentry.updated(entry["updated_at"])

    return Response(feed.atom_str(), mimetype="application/xml")

@app.route("/")
def api_root():
    """
    Return the about page
    """
    return send_file("index.html")

if __name__ == "__main__":
    app.run()
