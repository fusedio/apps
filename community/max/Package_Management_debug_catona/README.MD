<!--fused:preview-->
<p align="center"><img src="https://miro.medium.com/v2/resize:fit:1160/format:webp/0*Kt5_0uGLlCFAgbt6.png" width="600" alt="UDF preview image"></p>

<!--fused:readme-->
### Install a Package
This example shows how to install a python package in Fused.
To use this package add this inside your udf:

import sys;
env_name='testxenv';
sys.path.append(f"/mnt/cache/envs/{env_name}/lib/python3.13/site-packages")
