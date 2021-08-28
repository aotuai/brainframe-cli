"""Uploads the PyInstaller binary to our S3 bucket for storing releases, then creates
a CloudFront invalidation to make those changes live.
"""

import argparse
import os
import uuid
from io import BytesIO
from pathlib import Path

import boto3
from brainframe.cli import __version__
from brainframe.cli.print_utils import fail

ssm = boto3.client("ssm")
s3 = boto3.client("s3")
cloudfront = boto3.client("cloudfront")


_COMPANY_NAMES = ["aotu", "dilililabs"]


def main():
    stage = os.environ.get("STAGE", "dev")

    args = _parse_args()

    if not args.binary_path.exists():
        fail(f"Missing binary at '{args.binary_path}'. Has a build been run?")

    bucket_name = _get_parameter(
        f"/content-delivery/bucket/releases/{stage}/bucket-name"
    )

    # Upload the binary
    s3.upload_file(
        Filename=str(args.binary_path),
        Bucket=bucket_name,
        Key="releases/brainframe-cli/brainframe",
    )

    # Upload a latest tag, containing the latest version number
    version_tag_file = BytesIO(__version__.encode("utf-8"))
    s3.upload_fileobj(
        Fileobj=version_tag_file,
        Bucket=bucket_name,
        Key="releases/brainframe-cli/latest",
    )

    for company_name in _COMPANY_NAMES:
        distribution_id = _get_parameter(
            f"/content-delivery/cdn/{company_name}/{stage}/distribution-id"
        )
        cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                "Paths": {
                    "Quantity": 1,
                    "Items": ["/releases/brainframe-cli/*"],
                },
                "CallerReference": str(uuid.uuid4()),
            },
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Uploads the PyInstaller binary to the releases bucket and makes "
        "the change live"
    )
    parser.add_argument(
        "--binary-path",
        help="A path to the binary to upload",
        type=Path,
        default=Path("dist/brainframe"),
    )

    return parser.parse_args()


def _get_parameter(name: str) -> str:
    response = ssm.get_parameter(Name=name)
    return response["Parameter"]["Value"]


if __name__ == "__main__":
    main()
