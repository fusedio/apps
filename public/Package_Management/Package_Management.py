import streamlit as st
import time # This should be on top if you want the spinner to happen
import fused
st.title("Install a Package")
is_loggedin=False
try:
    name = fused.api.whoami()['name']
    st.success(f'You are successfully logged in as {name}.')
    is_loggedin=True
except:
    st.error('You are currently not logged in to Fused.')

if 'button1' not in st.session_state:
    st.session_state.button1 = True
if 'button2' not in st.session_state:
    st.session_state.button2 = True
if 'expanded' not in st.session_state:
    st.session_state.expanded = True

def click_button(button_arg):
    st.session_state[button_arg] = False
    
@fused.udf 
def list_folders(path="/mount/envs/"):
    import os
    import pandas as pd
    if os.path.exists(path):
        folders = [f for f in os.listdir(path)]
        return pd.DataFrame(folders, columns=['Environments'])
    else: 
        return  pd.DataFrame({'error': ["Path does not exist"]})

@fused.udf
def pip_freeze(env='demo_env', mnt_path="/mount/envs/"):
    import pandas as pd
    utils = fused.load('https://github.com/fusedio/udfs/tree/d0f4a86/public/common/').utils
    r = utils.run_cmd(
            f"{mnt_path}{env}/bin/python -m pip freeze", communicate=True
        )
    df = pd.DataFrame({'status': [str(i.decode('utf-8')) for i in r]})
    return df

@fused.udf
def udf(name='numpy', env='demo_env', mnt_path="/mount/envs/", packages_path="/lib/python3.11/site-packages"):
    import pandas as pd
    import loguru
    utils = fused.load('https://github.com/fusedio/udfs/tree/d0f4a86/public/common/').utils
    # install_module = utils.install_module
    def install_module(
        name,
        env="demo_env",
        mnt_path="/mount/envs/",
        packages_path="/lib/python3.11/site-packages",
    ):
        import os
        import sys
        path = f"{mnt_path}{env}{packages_path}"
        sys.path.append(path)
        if not os.path.exists(path):
            utils.run_cmd(f"python3.11 -m venv  {mnt_path}{env}", communicate=True)
        return utils.run_cmd(
            f"{mnt_path}{env}/bin/python -m pip install {name}", communicate=True
        )
    
    r = install_module(name=name, env=env, mnt_path=mnt_path)
    loguru.logger.info(r)
    # print(r) 
    df = pd.DataFrame({'status': [str(i.decode('utf-8')) for i in r]})
    df['status'] = df['status']
    return df


if is_loggedin:
    # User Inputs
    name = st.text_input("Module Name", value="numpy")
    env = st.text_input("Environment", value="demo_env")
    mnt_path = st.text_input("Mount Path", value="/mount/envs/")     
    # with st.expander(f"See all Environment options in {mnt_path}", expanded=False):
    place_holder0 = st.empty()
    x =  place_holder0.button(f"Environments Details",on_click=click_button, args=['button2'])
    if x:
        with place_holder0.status(f"Environments in `{mnt_path}`", expanded=st.session_state.expanded):
            st.session_state.expanded=True
            time.sleep(0.01) 
            from datetime import datetime
            cache_id = datetime.now()
            st.write(fused.run(list_folders, path=mnt_path, cache_id=cache_id))
            st.markdown(f'**List of packages in `{env}`**')
            try:
                result = fused.run(pip_freeze(env=env, mnt_path=mnt_path, cache_id=cache_id))        
                success =st.success(f'{result.values[0][0]}')
            except:
                success =st.warning(f'{mnt_path}{env} is empty or not accessable.')
    # mode = st.radio("Execution Mode", ('Real-time', 'Batch'))
    place_holder = st.empty()
    place_holder.button('Submit', on_click=click_button, disabled= not st.session_state.button1, args=['button1'])
    if not st.session_state.button1:
        st.session_state.button1=True
        mode='Batch'
        if mode == 'Batch': 
            with place_holder.status(f"Install {name}", expanded=True):
                time.sleep(0.01) 
                result = udf(name=name, env=env, mnt_path=mnt_path).run_remote()
                st.session_state.button1=True
                job_url = fused.options.base_url.replace('server/v1',f'job_status/{result.job_id}')
                st.markdown(f"[job_status]({job_url})") 
        else:
            with place_holder.status(f"Install {name} (realtime)", expanded=True):
                time.sleep(0.01)  
                result = fused.run(udf(name=name, env=env, mnt_path=mnt_path, cache_id=cache_id))   
                st.session_state.button1=True
                success = result.values[0][0]
                error = result.values[1][0]
                if success: 
                    st.success(success)
                if error: 
                    st.error(error)
    
        st.markdown("To use this package add this inside your udf:")
     
        st.code(f"""
            import sys;
            sys.path.append(f"/mount/envs/{env}/lib/python3.11/site-packages/")
    """)
        st.session_state.button1=True
        
