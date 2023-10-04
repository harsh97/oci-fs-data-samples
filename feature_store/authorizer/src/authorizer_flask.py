import io
import json
import os

import flask
from fdk import context, response

from authorizer import authorizer

app = flask.Flask(__name__)


def generate_apigw_json_payload() -> io.BytesIO:
    """
     Converts the headers payload received from various clients to that expected by function from apigw
    """
    headers = {k.lower(): v for k, v in flask.request.headers.items()}
    payload = {"type": "USER_DEFINED",
          "data": headers}
    # Setting this header like this as api gateway doesn't allow forwarding of headers enclosed in parentheses
    headers["(request-target)"] = headers["path"]
    return io.BytesIO(bytes(json.dumps(payload), 'utf-8'))


# call list feature stores api to invoke this
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def local_authorizer(_: str):
    ctx = context.InvokeContext(app_id="0", app_name="authorizer", fn_id="0", fn_name="authorizer", call_id="0",
                                config={"AUTHORIZED_GROUP_IDS": os.getenv("AUTHORIZED_GROUP_IDS")})
    fdk_resp: response.Response = authorizer(ctx, data=generate_apigw_json_payload())
    return flask.Response(response=fdk_resp.response_data, status=fdk_resp.status())
