# app.py (수정된 버전)
import streamlit as st
from auth import AuthManager, auth_page
from post import PostManager, create_post_form, display_posts_feed, post_detail_page
from sidebar import sidebar_navigation, profile_page, my_posts_page, liked_posts_page, all_users_page
from follow import FollowManager
from factory_manager import FactoryManager
from factory_dashboard import factory_dashboard_page, factory_detail_page
from factory_integration import integrate_factory_with_social_feed, schedule_factory_monitoring
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows

# 마이너스 부호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# Streamlit 페이지 설정
st.set_page_config(
    page_title="소셜 서비스 + Factory Monitor", 
    page_icon="📱",
    layout="wide"
)

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
if 'selected_factory_id' not in st.session_state:
    st.session_state.selected_factory_id = None

# 매니저 초기화
auth_manager = AuthManager()
post_manager = PostManager()
follow_manager = FollowManager()
factory_manager = FactoryManager()

# 자동 모니터링 시작 (선택사항)
if 'monitoring_started' not in st.session_state:
    st.session_state.monitoring_started = True
    # 백그라운드 모니터링 (5분마다)
    # schedule_factory_monitoring(factory_manager, post_manager, 300)

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
    elif current_page == 'factory_dashboard':
        factory_dashboard_page(factory_manager, post_manager)
    elif current_page == 'factory_detail':
        factory_detail_page(factory_manager)
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
    
    # 팩토리 현황 요약 (상단에 표시)
    summary = factory_manager.get_factory_summary()
    if summary['total_factories'] > 0:
        with st.container():
            st.markdown("### 🏭 팩토리 현황 요약")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("총 팩토리", summary['total_factories'])
            with col2:
                st.metric("✅ 정상", summary['normal_count'])
            with col3:
                st.metric("⚠️ 경고", summary['warning_count'])
            with col4:
                st.metric("🔥 위험", summary['error_count'])
            with col5:
                if st.button("🏭 대시보드", type="primary"):
                    st.session_state.current_page = 'factory_dashboard'
                    st.rerun()
            
            # 위험 상황 알림
            if summary['error_count'] > 0:
                st.error(f"🚨 {summary['error_count']}개 팩토리에서 긴급 상황 발생! 즉시 확인이 필요합니다.")
            elif summary['warning_count'] > 0:
                st.warning(f"⚠️ {summary['warning_count']}개 팩토리에서 주의가 필요합니다.")
    
    st.write("---")
    
    # 빠른 팩토리 액션
    if summary['total_factories'] > 0:
        with st.expander("🔧 빠른 팩토리 제어", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 모든 팩토리 상태 업데이트"):
                    updated_count = 0
                    for factory_id in factory_manager.factories.keys():
                        factory_manager.update_factory_status(factory_id)
                        updated_count += 1
                    st.success(f"{updated_count}개 팩토리 상태가 업데이트되었습니다!")
                    st.rerun()
            
            with col2:
                if st.button("📱 소셜 피드에 팩토리 상태 동기화"):
                    integrate_factory_with_social_feed(post_manager, factory_manager)
                    st.success("팩토리 상태가 소셜 피드에 동기화되었습니다!")
                    st.rerun()
            
            with col3:
                if st.button("⚠️ 강제 이상 상황 테스트"):
                    if factory_manager.factories:
                        test_factory_id = list(factory_manager.factories.keys())[0]
                        factory_manager.update_factory_status(test_factory_id, force_abnormal=True)
                        st.warning("테스트용 이상 상황이 발생했습니다!")
                        st.rerun()
    
    st.write("---")
    
    # 게시물 작성 폼
    create_post_form(post_manager, st.session_state.username)
    
    # 피드 표시 (enhanced 버전 사용)
    display_enhanced_posts_feed(post_manager, st.session_state.username, auth_manager)

def display_enhanced_posts_feed(post_manager, current_username, auth_manager=None):
    """향상된 게시물 피드 표시"""
    st.subheader("📱 최신 게시물")
    
    # 피드 필터 옵션
    col_filter, col_count = st.columns([3, 1])
    with col_filter:
        feed_filter = st.selectbox(
            "피드 필터", 
            ["전체", "일반 포스트만", "팩토리 알림만", "긴급 상황만"]
        )
    with col_count:
        post_count = st.selectbox("표시 개수", [10, 20, 30, 50], index=1)
    
    posts = post_manager.get_posts_feed(post_count)
    
    # 필터링
    if feed_filter == "일반 포스트만":
        posts = posts[posts['username'] != "🏭_Factory_System"]
    elif feed_filter == "팩토리 알림만":
        posts = posts[posts['username'] == "🏭_Factory_System"]
    elif feed_filter == "긴급 상황만":
        emergency_posts = []
        for _, post in posts.iterrows():
            if post['username'] == "🏭_Factory_System":
                try:
                    if isinstance(post['content'], str):
                        content_data = json.loads(post['content'])
                        if content_data.get('priority') in ['emergency', 'high']:
                            emergency_posts.append(post)
                except:
                    pass
        if emergency_posts:
            import pandas as pd
            posts = pd.DataFrame(emergency_posts)
        else:
            posts = pd.DataFrame()
    
    if len(posts) == 0:
        st.write("표시할 게시물이 없습니다.")
        if feed_filter == "긴급 상황만":
            st.info("현재 긴급 상황이 없습니다. 🎉")
        return
    
    # enhanced_post_display에서 import
    from enhanced_post_display import display_enhanced_post
    
    for _, post in posts.iterrows():
        display_enhanced_post(post.to_dict(), post_manager, current_username, show_actions=True, auth_manager=auth_manager)

# 메인 라우팅
if st.session_state.logged_in:
    main_page()
else:
    auth_page(auth_manager)