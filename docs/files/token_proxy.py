#!/usr/bin/env python3
"""SANS Holiday Hack Challenge 2019 - Retrieve Scraps of Paper from Server."""
import requests
from flask import Flask, Response
app = Flask(__name__)


@app.route("/")
def token():
    """Return a token."""
    url = 'https://studentportal.elfu.org/validator.php'
    token = requests.Session().get(url).text
    # Put the token in the body, input tag, and header.
    resp = Response(
        f'Token:{token}\n'
        '<form>\n'
        f'  <input type="hidden" id="token" name="token" value="{token}"/>\n'
        '</form>\n'
    )
    resp.headers['token'] = token
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0')
