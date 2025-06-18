import json
import boto3
import logging


# warm init
ssm = boto3.client("ssm", region_name="us-east-2")
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # or DEBUG, WARNING, ERROR


# helpers
def err_response(code: int, message: str) -> dict:
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "error": {
                    "message": message,
                }
            }
        ),
    }


def get_store_host(ssm, env: str, business: str, store: str) -> str | None:
    path = f"/{env}/business/{business}/store/{store}/host"
    res = ssm.get_parameter(Name=path, WithDecryption=True)
    return res.get("Parameter", {}).get("Value")


def get_all_hosts(ssm, env: str, business: str) -> list[str]:
    path = f"/{env}/business/{business}/"
    next_tok = None
    hosts = []

    while True:
        kwargs = {"Path": path, "Recursive": True, "WithDecryption": True}
        if next_tok:
            kwargs["NextToken"] = next_tok

        res = ssm.get_parameters_by_path(**kwargs)

        for param in res.get("Parameters", []):
            if param["Name"].endswith("/host"):
                hosts.append(param["Value"])

        next_tok = res.get("NextToken")

        if not next_tok:
            break

    return hosts


def lambda_handler(event, context):
    # payload
    business = event.get("business")
    store = event.get("store")

    # payload guards
    if not isinstance(business, str) or not business.strip():
        return err_response(400, "Invalid business.")

    if not isinstance(store, str) or not store.strip():
        return err_response(400, "Invalid store.")

    # get param
    try:
        if store == "*":
            value = get_all_hosts(ssm, "dev", business)
        else:
            value = get_store_host(ssm, "dev", business, store)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"value": value}),
        }

    except ssm.exceptions.ParameterNotFound:
        return err_response(404, "Not found.")

    except Exception as e:
        return err_response(500, f"An unknown system error occurred {e}.")
