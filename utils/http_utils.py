import requests

def request_handler(url, method, data=None, headers=None, params=None):
    try:
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f'Invalid HTTP method: {method}')

        # Raise an exception for 4xx and 5xx status codes
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.ConnectionError as conn_err:
        print(f'Error connecting to the server: {conn_err}')
    except requests.exceptions.Timeout as timeout_err:
        print(f'Request timed out: {timeout_err}')
    except requests.exceptions.RequestException as req_err:
        print(f'An error occurred during the request: {req_err}')