import streamlit as st
from auth import AuthManager, auth_page
from post import PostManager, create_post_form, display_posts_feed, post_detail_page
from sidebar import sidebar_navigation, profile_page, my_posts_page, liked_posts_page

# Streamlit 페이지 설정
st.set_page_config(page_title="소셜 서비스", page_icon="📱")

# 초기 상태 설정
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# 매니저 초기화
auth_manager = AuthManager()
post_manager = PostManager()

def main_page():
    """메인 페이지 (로그인 후)"""
    # 사이드바 네비게이션
    current_page = sidebar_navigation()
    
    # 페이지 라우팅
    if current_page == 'home':
        home_page()
    elif current_page == 'profile':
        profile_page(auth_manager, post_manager, st.session_state.username)
    elif current_page == 'my_posts':
        my_posts_page(post_manager, st.session_state.username)
    elif current_page == 'liked_posts':
        liked_posts_page(post_manager, st.session_state.username)
    elif current_page == 'post_detail':
        post_detail_page(post_manager, st.session_state.username)

def home_page():
    """홈 페이지 (피드)"""
    st.title("🏠 홈")
    
    # 환영 메시지
    st.write(f"환영합니다, {st.session_state.username}님!")
    st.write("---")
    
    # 게시물 작성 폼
    create_post_form(post_manager, st.session_state.username)
    
    # 게시물 피드 표시
    display_posts_feed(post_manager, st.session_state.username)

# 메인 라우팅
if st.session_state.logged_in:
    main_page()
else:
    auth_page(auth_manager)