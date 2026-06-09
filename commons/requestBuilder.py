import gzip
import json
import logging
import os
import time
import calendar
import io
import zlib
import requests
from string import Template
from functools import reduce
import concurrent.futures
from commons.jsonBuilder import write_json_file
from commons.csvBuilder import write_responses_in_csv
from environment import get_execute_flag, get_ssl_verify

logger = logging.getLogger(__name__)


def response_from_auth(method, url, payload):
    if not get_execute_flag():
        logger.debug("Debug mode — using fake token, no auth request sent.")
        return {"access_token": "TOKEN_FAKE"}

    headers = {
        'requestTraceId': f"ThunderAuth-{method}",
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        logger.debug("Auth attempt %d/%d: method=%s url=%s", attempt, max_attempts, method, url)
        response = select_request("", method, url, "", payload, headers)
        if response.status_code == 200:
            return response.json()
        logger.warning("Auth attempt %d/%d failed (status=%s)", attempt, max_attempts, response.status_code)

    raise RuntimeError(
        f"Authentication failed after {max_attempts} attempt(s) — check if the auth service is running."
    )


def select_token_type(auth_url, auth_method, auth_type, auth_payload, token):
    if auth_type == "Bearer":
        return get_access_token(token, auth_method, auth_url, auth_payload)
    return token


def get_access_token(key, method, url, payload):
    data = response_from_auth(method, url, payload)
    if key in data:
        return str(data[key])
    logger.error("Auth response does not contain key '%s'. Check the auth_token field in your config.", key)
    return None


def create_header(data_header, auth_url, auth_method, auth_type, auth_payload, token, request_trace_id, auth_header=None, zip_payload_needed=None):
    new_header = []
    new_token = select_token_type(auth_url, auth_method, auth_type, auth_payload, token)
    headers = {
        "requestTraceId": request_trace_id,
        "Authorization": "{} {}".format(auth_type, new_token),
        "Content-Type": "application/json",
        "accept": "application/json",
        "x-timestamp": str(calendar.timegm(time.gmtime())),
    }

    for header in data_header:
        if auth_header:
            for key, value in auth_header.items():
                header[key] = value
        new_header.append({**headers, **header})
    return new_header


def zip_payload(payload: str) -> bytes:
    file = io.BytesIO()
    g = gzip.GzipFile(fileobj=file, mode='w')
    if type(payload) is str:
        g.write(bytes(payload, "utf-8"))
    else:
        g.write(payload)
    g.close()
    return file.getvalue()


def send_requests_in_parallel(request_name, method, url, data, payload, headers, chunk_size=10, max_workers=None):
    request_list = [(method, url, data, headers, p, request_name, idx, e, []) for idx, (e, p) in
                    enumerate(zip(payload, data))]
    # divide the requests into chunks
    chunks = [request_list[i:i + chunk_size] for i in range(0, len(request_list), chunk_size)]

    responses = []
    # create a thread pool to process the chunks
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for chunk in chunks:
            # submit the requests for each chunk
            future_to_request = {executor.submit(exec_request, *req): req for req in chunk}
            # iterate over the completed futures
            for future in concurrent.futures.as_completed(future_to_request):
                try:
                    response = future.result()
                    responses.append(response)
                except Exception as e:
                    logger.error("Error during parallel request: %s", e)
    return responses


def send_request(request_name, method, url, headers, payload, data, multiple_request=False, request_through_middleware_api=False, zip_payload_needed=None):
    if multiple_request and type(payload) is list:
        payload = [zip_payload(body) if zip_payload_needed else body for body in payload]
    else:
        headers = reduce(lambda a, b: dict(a, **b), headers)
        payload = zip_payload(payload) if zip_payload_needed else payload

    if not get_execute_flag():
        print_request_and_exit(request_name, method, url, headers, payload, zip_payload_needed)
    else:
        response = select_request(request_name, method, url, data, payload, headers, multiple_request)
        evaluate_response(payload, response, request_name, multiple_request, request_through_middleware_api)
        return response

def exec_request(*args):
    method, url, data, headers, payload, request_name, idx, element, response = args
    params = dict()
    if type(headers) is list:
        new_headers = headers[idx]
        url_list = Template(url).substitute(data[idx]).format(data[idx].get("user_id"))
    else:
        new_headers = headers
        url_list = Template(url).substitute(data[0])
    params['requestTraceId'] = f"{new_headers['requestTraceId']}_part_{idx + 1}_of_{len(data)}"
    new_headers['requestTraceId'] = f"{new_headers['requestTraceId']}_part_{idx + 1}_of_{len(data)}"
    new_headers['x-timestamp'] = str(calendar.timegm(time.gmtime()))
    res = requests.request(method, url_list, data=element, headers=new_headers)
    logger.info("Sending requestTraceId=%s", new_headers['requestTraceId'])
    write_responses_in_csv(element, request_name, params, True, False)
    return res

def select_request(request_name, method, url, data, payload, headers, multiple_request=False):
    if method == "get":
        return [
            requests.get(url, headers=headers, params=p, verify=get_ssl_verify())
            for p in payload
        ]
    if method in {"post", "put", "delete", "patch"}:
        if multiple_request:
            return send_requests_in_parallel(request_name, method, url, data, payload, headers)
        return requests.request(method, url, data=payload, headers=headers, verify=get_ssl_verify())
    logger.warning("HTTP method '%s' is not supported.", method)
    return None


def evaluate_response(payload, responses, request_name, multiple_request, request_through_middleware_api):
    if type(responses) == list:
        for idx, response in enumerate(responses):
            print_result(payload[idx], response, request_name, multiple_request, request_through_middleware_api)
    else:
        print_result(payload, responses, request_name, multiple_request, request_through_middleware_api)

def print_request_and_exit(request_name, method, url, headers, body_request, zip_payload_needed):
    logger.info("DEBUG MODE — fake token in use, no requests sent. Add -e to execute.")
    if type(body_request) is not list:
        unzipped_payload = zlib.decompress(body_request, 16 + zlib.MAX_WBITS) if zip_payload_needed else body_request
        if type(unzipped_payload) is not bytes:
            unzipped_payload = bytearray(unzipped_payload, "utf-8")
        logger.info("METHOD: %s", method)
        logger.info("URL: %s", url)
        logger.info("HEADERS: %s", headers)
        logger.info("PAYLOAD:\n%s", unzipped_payload.decode("utf-8"))
        write_json_file(f'\n\n{unzipped_payload.decode("utf-8")}\n', request_name)
    else:
        count = 1
        for req in body_request:
            unzipped_payload = zlib.decompress(req, 16 + zlib.MAX_WBITS) if zip_payload_needed else req
            current_headers = headers[count - 1] if type(headers) is list else headers
            logger.info("METHOD: %s | URL: %s", method, url)
            logger.info("HEADERS: %s", current_headers)
            if type(unzipped_payload) is not bytes and type(unzipped_payload) is not dict:
                unzipped_payload = bytearray(unzipped_payload, "utf-8")
                logger.info("PAYLOAD:\n%s", unzipped_payload.decode("utf-8"))
                write_json_file(f'\n\n{unzipped_payload.decode("utf-8")}\n', request_name + "req" + str(count))
            if type(unzipped_payload) is bytes:
                logger.info("PAYLOAD:\n%s", unzipped_payload.decode("utf-8"))
                write_json_file(f'\n\n{unzipped_payload.decode("utf-8")}\n', request_name + "req" + str(count))
            if type(unzipped_payload) is dict:
                logger.info("PAYLOAD: %s", unzipped_payload)
                write_json_file(f'\n\n{unzipped_payload}\n', request_name + "req" + str(count))
            count = count + 1


def _format_payload(payload) -> str:
    if type(payload) is str:
        return payload.replace('\n', '').replace(' ', '')
    if type(payload) is dict:
        return json.dumps(payload).replace('\n', '').replace(' ', '')
    return ''.join(payload.decode("utf-8").split())


def print_result(payload, response, request_name, multiple_request, request_through_middleware_api):
    params = dict()
    status = response.status_code
    trace_id = response.request.headers.get('requestTraceId')
    request_body = _format_payload(payload)

    error_context = (
        "status=%s url=%s traceId=%s request=%s response=%s",
        status, response.request.url, trace_id, request_body, response.content,
    )

    if status == 400:
        logger.error("Bad Request (400) — check country support, headers, and template payload.")
        logger.error(*error_context)
    elif status == 401:
        logger.error("Unauthorized (401) — check your credentials.")
        logger.error(*error_context)
    elif status == 403:
        logger.error("Forbidden (403) — authorization denied.")
        logger.error(*error_context)
    elif status == 404:
        logger.error("Not Found (404).")
        logger.error(*error_context)
    elif status == 500:
        logger.error("Internal Server Error (500) — check if the target service is running.")
        logger.error(*error_context)
    elif status in range(200, 220):
        logger.info("Success (%s) — traceId=%s request=%s", status, trace_id, request_body)
        params['requestTraceId'] = trace_id
        if not multiple_request:
            write_responses_in_csv(payload, request_name, params, multiple_request, request_through_middleware_api)
        logger.info("Report saved to csv_generated/ — filter by requestTraceId.")
    else:
        logger.info("Finished — status=%s traceId=%s request=%s", status, trace_id, request_body)

    return response
