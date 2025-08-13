import pandas as pd
import streamlit as st
from datetime import datetime

class AuthManager:
    def __init__(self, csv_file='users.csv'):
        self.csv_file = csv_file
        self.df = self.load_users()
    
    def load_users(self):
        """CSV 파일에서 사용자 데이터 로드"""
        try:
            return pd.read_csv(self.csv_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=['id', 'username', 'password', 'created_at'])
    
    def save_users(self):
        """사용자 데이터를 CSV 파일에 저장"""
        self.df.to_csv(self.csv_file, index=False)
    
    def save_users(self):
        """사용자 데이터를 CSV 파일에 저장"""
        self.df.to_csv(self.csv_file, index=False)
    
    def user_exists(self, username):
        """사용자명 중복 체크"""
        return (self.df["username"] == username).any()
    
    def get_next_id(self):
        """새로운 사용자 ID 생성"""
        if len(self.df) == 0:
            return 1
        else:
            return self.df['id'].max() + 1
    
    def register_user(self, username, password):
        """회원가입 처리"""
        if not username or not password:
            return False, "사용자명과 비밀번호를 입력하세요"
        
        if self.user_exists(username):
            return False, "이미 존재하는 사용자명입니다"
        
        new_user = {
            'id': self.get_next_id(),
            'username': username,
            'password': password,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.df = pd.concat([self.df, pd.DataFrame([new_user])], ignore_index=True)
        self.save_users()
        
        return True, "회원가입이 완료되었습니다!"
    
    def login_user(self, username, password):
        """로그인 처리"""
        if not username or not password:
            return False, "사용자명과 비밀번호를 입력하세요"
        
        if not self.user_exists(username):
            return False, "존재하지 않는 사용자명입니다"
        
        user_row = self.df[self.df["username"] == username]
        stored_password = str(user_row["password"].iloc[0])
        
        if password == stored_password:
            return True, f"환영합니다, {username}님!"
        else:
            return False, "비밀번호가 틀렸습니다"

def signup_form(auth_manager):
    """회원가입 폼"""
    st.header("회원가입")
    
    input_username = st.text_input("사용자명을 입력하세요", key="signup_username")
    input_password = st.text_input("비밀번호를 입력하세요", type='password', key="signup_password")
    
    if st.button("회원가입 완료", key="signup_btn"):
        success, message = auth_manager.register_user(input_username, input_password)
        
        if success:
            st.success(message)
            st.session_state.show_signup = False  # 회원가입 후 로그인 폼으로
            st.rerun()
        else:
            st.error(message)

def login_form(auth_manager):
    """로그인 폼"""
    st.header("로그인")
    
    username = st.text_input("사용자명", key="login_username")
    password = st.text_input("비밀번호", type='password', key="login_password")
    
    if st.button("로그인하기", key="login_btn"):
        success, message = auth_manager.login_user(username, password)
        
        if success:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(message)
            st.rerun()
        else:
            st.error(message)

def auth_page(auth_manager):
    """인증 페이지 (로그인/회원가입)"""
    st.title("소셜 서비스")
    
    # 로그인/회원가입 전환 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인", use_container_width=True, key="switch_login"):
            st.session_state.show_signup = False
            st.rerun()
    with col2:
        if st.button("회원가입", use_container_width=True, key="switch_signup"):
            st.session_state.show_signup = True
            st.rerun()
    
    st.write("---")
    
    # 선택된 폼 표시
    if st.session_state.get('show_signup', False):
        signup_form(auth_manager)
    else:
        login_form(auth_manager)