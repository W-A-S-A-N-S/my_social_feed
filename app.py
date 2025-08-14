import streamlit as st
from auth import AuthManager, auth_page
from post import PostManager, create_post_form, display_posts_feed, post_detail_page
# 아래 라인을 수정
from sidebar import sidebar_navigation, profile_page, my_posts_page, liked_posts_page, all_users_page
from follow import FollowManager

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
if 'target_user_id' not in st.session_state:
    st.session_state.target_user_id = None

# 매니저 초기화
auth_manager = AuthManager()
post_manager = PostManager()
follow_manager = FollowManager()

def main_page():
    """메인 페이지 (로그인 후)"""
    # 사이드바 네비게이션
    current_page = sidebar_navigation()
    
    # 페이지 라우팅
    if current_page == 'home':
        home_page()
    elif current_page == 'profile':
        profile_page(auth_manager, post_manager, follow_manager, st.session_state.username)
    elif current_page == 'my_posts':
        my_posts_page(post_manager, st.session_state.username, auth_manager)
    elif current_page == 'liked_posts':
        liked_posts_page(post_manager, st.session_state.username, auth_manager)
    elif current_page == 'all_users':
        all_users_page(auth_manager, post_manager, follow_manager)
    elif current_page == 'view_profile':
        target_username = auth_manager.get_username_by_id(st.session_state.target_user_id)
        if target_username:
            profile_page(auth_manager, post_manager, follow_manager, target_username)
        else:
            st.error("사용자를 찾을 수 없습니다.")
    elif current_page == 'post_detail':
        post_detail_page(post_manager, st.session_state.username, auth_manager)

def home_page():
    """홈 페이지 (피드)"""
    st.title("🏠 홈")
    
    st.write(f"환영합니다, {st.session_state.username}님!")
    st.write("---")
    
    create_post_form(post_manager, st.session_state.username)
    
    display_posts_feed(post_manager, st.session_state.username, auth_manager)

# 메인 라우팅
if st.session_state.logged_in:
    main_page()
else:
    auth_page(auth_manager)