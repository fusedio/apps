import streamlit as st
import fused

st.header("IAM policy to connect Fused to your own S3 bucket")

st.text("This app generates an IAM policy for you to apply to your own S3 bucket so it can be accessed through the Fused system.")

try:
    api = fused.api.FusedAPI()
    name = fused.api.whoami()['name']
    st.success(f'You are successfully logged in as {name}.')
    is_loggedin=True
except:
    st.error("You are currently not logged in to Fused. [Login](https://www.fused.io/api/auth/login?returnTo=%2Fworkbench%2Fapps) to access this Fused App")
    is_loggedin=False

if is_loggedin:
    instances = api._list_realtime_instances()
    
    instance_name = st.selectbox("Realtime instance name", [i['name'] for i in instances])
    
    s3_bucket_name = st.text_input("S3 bucket name", "your-bucket-name")
    
    st.header("Generated IAM policy for your bucket")
    
    # TODO: This may be incorrect for some instances
    instance_account_id = 926411091187
    for i in instances:
        if i['name'] == instance_name:
            if 'account_id' in i and i['account_id']:
                instance_account_id = i['account_id']
    
    st.code(f"""
    {{
        "Sid": "Allow object access by Fused {instance_name} account",
        "Effect": "Allow",
        "Principal": {{
            "AWS": [
                "arn:aws:iam::{instance_account_id}:role/rt-production-{instance_name}",
                "arn:aws:iam::{instance_account_id}:role/ec2_job_task_role-v2-production-{instance_name}",
                "arn:aws:iam::926411091187:role/fused_server_role_prod_us_west_2"
            ]
        }},
        "Action": [
            "s3:ListBucket",
            "s3:GetObjectAttributes",
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject"
        ],
        "Resource": [
            "arn:aws:s3:::{s3_bucket_name}/*",
            "arn:aws:s3:::{s3_bucket_name}/"
        ]
    }}""", language="json")
