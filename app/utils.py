# utils.py
from flask import jsonify
import pandas as pd
from itertools import product

def create_response(status, data=None, error=None, status_code=200, error_code=None):
    """
    Creates a response dictionary with the given status, data, and error information.

    Args:
        status (bool or str): The status of the response.
        data (any, optional): The data to include in the response. Defaults to None.
        error (str, optional): The error message to include in the response. Defaults to None.
        status_code (int, optional): The HTTP status code of the response. Defaults to 200.
        error_code (any, optional): The error code to include in the response. Defaults to None.

    Returns:
        tuple: A tuple containing the response dictionary and the HTTP status code.

    Examples:
        response = create_response(True, data={"message": "Success"})
        # Returns: ({'status': 'true', 'data': {'message': 'Success'}}, 200)

        response = create_response(False, error="Invalid input", status_code=400, error_code=1001)
        # Returns: ({'status': 'false', 'error': {'message': 'Invalid input', 'code': 1001}}, 400)
    """
    response = {"status": str(status).lower() if isinstance(status, bool) else status}

    if data is not None:
        response["data"] = data

    if error is not None:
        response["error"] = {"message": str(error)}
        if error_code is not None:
            response["error"]["code"] = error_code.value

    return jsonify(response), status_code


def validate_request_data(data, required_properties):
    if missing_properties := [
        prop for prop in required_properties if prop not in data
    ]:
        raise ValueError(f"Missing properties in the request: {', '.join(missing_properties)}")

def generate_combinations(brand_names, search_queries=None, separator='-'):
    """
    Generate all combinations of brand names and search queries.

    Parameters:
        brand_names (list): List of brand names.
        search_queries (list): List of search queries.
        separator (str, optional): Separator between brand name and search query. Default is '-'.

    Returns:
        pd.DataFrame: DataFrame with columns 'brandName' and 'searchQuery'.
        list: List of strings with all combinations of brandName and searchQuery.
    """
    # Generate all combinations of brand names and search queries
    all_combinations = list(product(brand_names, search_queries))
    df = pd.DataFrame(all_combinations, columns=['brandName', 'searchQuery'])
    search_queries_list = [f"{brand}{separator}{query}" for brand, query in all_combinations]

    return df, search_queries_list
