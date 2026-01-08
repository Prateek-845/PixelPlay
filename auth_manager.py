import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import bcrypt

def load_config():
    with open('config.yaml') as file:
        return yaml.load(file, Loader=SafeLoader)

def save_config(config):
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def setup_authenticator():
    config = load_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator, config

def show_login_flow(authenticator, config):    
    left_spacer, login_col, right_spacer = st.columns([3, 2, 3])
    with login_col:
        authenticator.login()
        
        if st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please sign in to continue')
            
            with st.expander("Forgot Password?"):
                try:
                    username_forgot, email_forgot, new_password = authenticator.forgot_password(location='main')
                    if username_forgot:
                        st.success('Password reset initiated.')
                        st.code(f"Temporary Credential: {new_password}")
                        save_config(config)
                except Exception as e:
                    st.error(e)

            with st.expander("Create Account"):
                with st.form("Register"):
                    new_email = st.text_input("Email Address")
                    new_username = st.text_input("Username")
                    new_password = st.text_input("Password", type="password")
                    submit_reg = st.form_submit_button("Register Account")
                    
                    if submit_reg:
                        if new_username and new_password and new_email:
                            if new_username in config['credentials']['usernames']:
                                st.error("Username Taken")
                            else:
                                try:
                                    hashed_bytes = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                                    hashed_pw = hashed_bytes.decode('utf-8')
                                    config['credentials']['usernames'][new_username] = {
                                        'name': new_username, 'email': new_email, 'password': hashed_pw
                                    }
                                    save_config(config)
                                    st.success("Account created successfully")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            st.error("All fields are required")