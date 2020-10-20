#!/usr/bin/env python3

"""
Github Notification RSS Feed
"""

from feedgen.feed import FeedGenerator
from requests.auth import HTTPBasicAuth
import requests

from flask import Flask, Response

app = Flask(__name__)

@app.route("/<username>/<token>/.atom", methods=["GET"])
def api_rss(username: str, token: str):
    """
    Get the rss feed for a user/token combo
    """
    auth = HTTPBasicAuth(username, token)
    endpoint = 'https://api.github.com/notifications?all=true'

    r = requests.get(endpoint, auth=auth)
    if r.status_code != 200:
        # Report error back to client
        return r.text, r.status_code

    fg = FeedGenerator()
    fg.id(endpoint)
    fg.title("Github Notifications")
    fg.language("en")

    for entry in r.json():
        fe = fg.add_entry(order="append")
        fe.id(entry['url'])
        fe.title(f"[{entry['subject']['type']}] {entry['subject']['title']}")
        fe.link(href=entry["subject"]["url"])
        fe.updated(entry["updated_at"])

    return Response(fg.atom_str(), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
