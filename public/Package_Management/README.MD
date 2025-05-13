<!--fused:pin=6-->
<!--fused:preview-->
<p align="center"><img src="https://fused-magic.s3.amazonaws.com/thumbnails/apps-public/Package_Management.png" width="600" alt="UDF preview image"></p>

<!--fused:tags-->
Tags: `udf` `form`

<!--fused:readme-->
### Install a Package
This example shows how to install a python package in Fused.
To use this package add this inside your udf:

import sys;
env_name='testxenv';
sys.path.append(f"/mnt/cache/envs/{env_name}/lib/python3.13/site-packages")
