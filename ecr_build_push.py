#!/usr/bin/env python3
"""
Create ECR repository (if missing), build the pdd-dashboard Docker image locally,
and push it to ECR for use in Kubernetes (e.g. EKS) deployment.

Requires: boto3, AWS CLI configured, Docker running.
Usage:
  pip install boto3
  python ecr_build_push.py [--repo REPO] [--region REGION] [--tag TAG]
"""
# cd kuldeep_lambda_model_payload/pddAnalysisDashboard

# # Default: repo pdd-dashboard, tag 1.0, region from AWS_DEFAULT_REGION or us-east-1
# python ecr_build_push.py

# # Custom repo, region, and tag
# python ecr_build_push.py --repo pdd-dashboard --region us-east-1 --tag 1.0

# # Repo already exists
# python ecr_build_push.py --skip-create

import argparse
import os
import subprocess
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


def get_aws_account_id():
    """Get current AWS account ID."""
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]


def ensure_ecr_repository(region: str, repo_name: str) -> None:
    """Create ECR repository if it does not exist."""
    ecr = boto3.client("ecr", region_name=region)
    try:
        ecr.create_repository(repositoryName=repo_name)
        print(f"Created ECR repository: {repo_name}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "RepositoryAlreadyExistsException":
            print(f"ECR repository already exists: {repo_name}")
        else:
            raise


def run(cmd: list[str], cwd: Path | None = None) -> None:
    """Run command; raise on failure."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def ecr_login(region: str, account_id: str) -> None:
    """Log Docker into ECR."""
    result = subprocess.run(
        ["aws", "ecr", "get-login-password", "--region", region],
        capture_output=True,
        text=True,
        check=True,
    )
    password = result.stdout.strip()
    registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com"
    subprocess.run(
        ["docker", "login", "--username", "AWS", "--password-stdin", registry],
        input=password,
        capture_output=True,
        text=True,
        check=True,
    )
    print(f"Docker logged in to {registry}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create ECR repo, build and push pdd-dashboard image to ECR."
    )
    parser.add_argument(
        "--repo",
        default="pdd-dashboard",
        help="ECR repository name (default: pdd-dashboard)",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="AWS region (default: AWS_DEFAULT_REGION or us-east-1)",
    )
    parser.add_argument(
        "--tag",
        default="1.0",
        help="Image tag (default: 1.0)",
    )
    parser.add_argument(
        "--skip-create",
        action="store_true",
        help="Skip creating ECR repository (use if it already exists)",
    )
    args = parser.parse_args()

    region = args.region or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    script_dir = Path(__file__).resolve().parent

    # 1. Create ECR repository
    if not args.skip_create:
        ensure_ecr_repository(region, args.repo)

    # 2. Get AWS account ID
    account_id = get_aws_account_id()
    ecr_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{args.repo}:{args.tag}"
    local_image = f"pdd-dashboard:{args.tag}"

    # 3. Docker login to ECR
    ecr_login(region, account_id)

    # 4. Build image (context = script dir = pddAnalysisDashboard)
    run(
        ["docker", "build", "-t", local_image, "."],
        cwd=script_dir,
    )

    # 5. Tag for ECR
    run(["docker", "tag", local_image, ecr_uri])

    # 6. Push to ECR
    run(["docker", "push", ecr_uri])

    print("\nDone. Use this image in your Kubernetes deployment (e.g. deployment.yaml):")
    print(f"  image: {ecr_uri}")
    print("  imagePullPolicy: Always")


if __name__ == "__main__":
    main()
