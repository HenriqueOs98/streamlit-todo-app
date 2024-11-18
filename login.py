# login.py
import streamlit as st
from auth import Authentication
import streamlit.components.v1 as components

def show_login_page():
    auth = Authentication()
    
    st.markdown("""
        <style>
        .google-btn {
            background-color: white;
            border: 1px solid #4285f4;
            border-radius: 4px;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            cursor: pointer;
            width: 100%;
            margin: 10px 0;
        }
        .google-btn img {
            width: 20px;
            margin-right: 10px;
        }
        .google-btn:hover {
            background-color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("""
            <div class="google-btn" onclick="googleSignIn()">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg"/>
                <span>Sign in with Google</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")  
        
        tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Reset Password"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if auth.sign_in(email, password):
                        st.success("Logged in successfully!")
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Sign Up")
                
                if submit and new_password == confirm_password:
                    if auth.sign_up(new_email, new_password):
                        st.success("Account created successfully!")
                    else:
                        st.error("Could not create account")
        
        with tab3:
            with st.form("reset_form"):
                reset_email = st.text_input("Email")
                submit = st.form_submit_button("Reset Password")
                
                if submit:
                    if auth.reset_password(reset_email):
                        st.success("Password reset email sent!")
                    else:
                        st.error("Could not send reset email")

        # Add Google Sign-In JavaScript
        components.html("""
            <script src="https://www.gstatic.com/firebasejs/9.x.x/firebase-app.js"></script>
            <script src="https://www.gstatic.com/firebasejs/9.x.x/firebase-auth.js"></script>
            <script>
                const firebaseConfig = {
                    apiKey: "%s",
                    authDomain: "%s",
                    projectId: "%s",
                };
                
                firebase.initializeApp(firebaseConfig);
                
                function googleSignIn() {
                    const provider = new firebase.auth.GoogleAuthProvider();
                    firebase.auth().signInWithPopup(provider)
                        .then((result) => {
                            const credential = result.credential;
                            const token = credential.accessToken;
                            window.parent.postMessage(
                                {type: 'GOOGLE_SIGN_IN', token: token},
                                '*'
                            );
                        }).catch((error) => {
                            console.error('Error:', error);
                        });
                }
                
                window.addEventListener('message', function(event) {
                    if (event.data.type === 'GOOGLE_SIGN_IN') {
                        fetch('/_stcore/component-communication', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                token: event.data.token,
                                componentId: '%s'
                            })
                        });
                    }
                });
            </script>
        """ % (
            st.secrets["firebase"]["apiKey"],
            st.secrets["firebase"]["authDomain"],
            st.secrets["firebase"]["projectId"],
            components.get_component_id()
        ), height=0)
        
        if 'google_token' in st.session_state:
            if auth.sign_in_with_google(st.session_state.google_token):
                st.success("Signed in with Google successfully!")
                del st.session_state.google_token
            else:
                st.error("Google sign-in failed")