from dataclasses import dataclass
import ipaddress
import os
import csv
import sys
import boto3


@dataclass
class Store:
    env: str
    business: str
    store: str
    addr: str


map = {
    "cactus": {
        "001": "10.3.66.100",
        "012": "10.12.66.100",
        "014": "10.7.66.100",
        "016": "10.6.66.100",
        "017": "10.13.66.100",
        "019": "10.8.66.100",
        "020": "10.5.66.100",
        "022": "10.18.66.100",
        "025": "10.23.66.100",
        "026": "10.24.66.100",
        "029": "10.14.66.100",
        "031": "10.4.66.100",
        "032": "10.17.66.100",
        "035": "10.31.66.100",
        "036": "10.27.66.100",
        "037": "10.28.66.100",
        "040": "10.33.66.100",
        "045": "10.35.66.100",
        "046": "10.19.66.100",
        "047": "10.40.66.100",
        "049": "10.44.66.100",
        "066": "10.45.66.100",
        "069": "10.47.66.100",
        "070": "10.33.67.100",
        "118": "10.16.66.100",
        "127": "10.26.66.100",
        "130": "10.15.66.100",
        "141": "10.32.66.100",
        "144": "10.37.66.100",
        "168": "10.49.66.100",
        "242": "10.34.66.100",
        "443": "10.36.66.100",
        "448": "10.42.66.100",
        "467": "10.50.66.100",
    },
    "kingtaps": {
        "051": "10.22.66.100",
        "054": "10.46.66.100",
        "055": "10.51.66.100",
        "071": "10.48.66.100",
        "453": "10.39.66.100",
        "456": "10.52.66.100",
    },
}


def main():
    # guard usage
    if not len(sys.argv) > 1:
        print("usage: python update-ssm.py <csv-path>")
        sys.exit(1)

    # guard csv
    csvpath = sys.argv[1]
    if not os.path.exists(csvpath):
        print(f"error: file not found {csvpath}")
        sys.exit(1)

    # data
    data = []
    with open(csvpath) as f:
        reader = csv.DictReader(f)

        for row in reader:
            print(row)
            data.append(
                Store(
                    env=row["env"],
                    business=row["business"],
                    store=row["store"],
                    addr=row["ip_address"],
                )
            )

    if len(data) == 0:
        print("error: datasource produced no data")
        sys.exit(1)

    # update ssm
    ssm = boto3.client("ssm")

    for x in data:
        path = f"/{x.env}/business/{x.business}/store/{x.store}/host"

        try:
            res = ssm.put_parameter(
                Name=path, Value=x.addr, Type="SecureString", Overwrite=True
            )

            # print(res)

            if res.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200:
                print(f"+ created param : {path}")
            else:
                print(f"! failed to create param : {path}")

        except Exception as e:
            print(f"! failed to create param {path} : {e}")


if __name__ == "__main__":
    main()
