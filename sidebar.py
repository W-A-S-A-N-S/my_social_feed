# sidebar.py (수정된 버전)
import streamlit as st
from post import display_post
from datetime import datetime
import os

def sidebar_navigation():
    """사이드바 네비게이션 메뉴"""
    st.sidebar.title("📱 소셜 서비스")
    st.sidebar.write(f"👋 {st.session_state.username}님")
    st.sidebar.write("---")
    
    # 네비게이션 메뉴
    menu_options = {
        "🏠 홈": "home",
        "👤 프로필": "profile", 
        "📝 내 게시물": "my_posts",
        "❤️ 좋아요한 게시물": "liked_posts",
        "🔍 모든 사용자": "all_users",
        "🏭 팩토리 대시보드": "factory_dashboard"  # 추가
    }
    
    current_page = st.session_state.get('current_page', 'home')
    
    for label, page_key in menu_options.items():
        # 팩토리 관련 메뉴는 특별히 강조
        if page_key == 'factory_dashboard':
            button_type = "primary" if current_page == page_key else "secondary"
        else:
            button_type = "secondary"
            
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{page_key}", type=button_type):
            st.session_state.current_page = page_key
            st.rerun()
    
    st.sidebar.write("---")
    
    # 팩토리 빠른 상태 (사이드바)
    display_factory_quick_status()
    
    st.sidebar.write("---")
    
    # 로그아웃 버튼
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ''
        st.session_state.show_signup = False
        st.session_state.current_page = 'home'
        # 리포스트 관련 세션 상태 초기화
        for key in list(st.session_state.keys()):
            if key.startswith('show_repost_'):
                del st.session_state[key]
        st.rerun()
    
    return current_page

def display_factory_quick_status():
    """사이드바에 팩토리 빠른 상태 표시"""
    try:
        # factory_manager가 있는지 확인
        if 'factory_manager' in globals() or hasattr(st.session_state, 'factory_manager'):
            from factory_manager import FactoryManager
            factory_manager = FactoryManager()
            
            summary = factory_manager.get_factory_summary()
            
            if summary['total_factories'] > 0:
                st.sidebar.subheader("🏭 팩토리 현황")
                
                # 상태별 개수 표시
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    st.sidebar.metric("정상", summary['normal_count'])
                    st.sidebar.metric("경고", summary['warning_count'])
                with col2:
                    st.sidebar.metric("위험", summary['error_count'])
                
                # 위험 상황 알림
                if summary['error_count'] > 0:
                    st.sidebar.error(f"🚨 {summary['error_count']}개 팩토리 위험!")
                elif summary['warning_count'] > 0:
                    st.sidebar.warning(f"⚠️ {summary['warning_count']}개 팩토리 주의")
                else:
                    st.sidebar.success("✅ 모든 팩토리 정상")
                
                # 빠른 액션 버튼
                if st.sidebar.button("🔄 상태 업데이트", key="sidebar_update"):
                    for factory_id in factory_manager.factories.keys():
                        factory_manager.update_factory_status(factory_id)
                    st.sidebar.success("업데이트 완료!")
                    st.rerun()
            
            else:
                st.sidebar.info("등록된 팩토리가 없습니다.")
                
    except Exception as e:
        st.sidebar.write("팩토리 상태 로딩 중...")

def profile_page(auth_manager, post_manager, follow_manager, username):
    """
    프로필 페이지 (다른 사용자의 프로필도 볼 수 있도록 수정)
    """
    is_my_profile = (username == st.session_state.username)
    
    if is_my_profile:
        st.title("👤 내 프로필")
    else:
        st.title(f"👤 {username}님의 프로필")
    
    user_info = auth_manager.df[auth_manager.df['username'] == username]
    user_id = user_info['id'].iloc[0] if len(user_info) > 0 else None

    # 사용자 정보
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # 현재 프로필 이모지 표시
        current_emoji = auth_manager.get_user_profile_emoji(username)
        st.markdown(f"<div style='font-size: 120px; text-align: center;'>{current_emoji}</div>", 
                   unsafe_allow_html=True)
    
    with col2:
        st.subheader(f"@{username}")
        
        # 가입일 정보
        user_info = auth_manager.df[auth_manager.df['username'] == username]
        if len(user_info) > 0:
            joined_date = user_info['created_at'].iloc[0]
            st.write(f"📅 가입일: {joined_date}")
            
    if not is_my_profile and user_id: 
        current_user_id = auth_manager.get_user_id(st.session_state.username)
        if current_user_id:
            if follow_manager.is_following(current_user_id, user_id):
                if st.button("언팔로우", key=f"unfollow_{user_id}", use_container_width=True):
                    success, message = follow_manager.unfollow_user(current_user_id, user_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                if st.button("팔로우", key=f"follow_{user_id}", type="primary", use_container_width=True):
                    success, message = follow_manager.follow_user(current_user_id, user_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                        
    st.write("---")

    # 통계 정보
    user_posts = post_manager.posts_df[post_manager.posts_df['username'] == username]
    total_posts = len(user_posts)
    total_likes_received = user_posts['like_count'].sum()
    total_reposts_received = user_posts['repost_count'].sum()

    # 팔로워/팔로잉 수 추가
    follower_count = follow_manager.get_follower_count(user_id) if user_id else 0
    following_count = follow_manager.get_following_count(user_id) if user_id else 0
    
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
    with col_stat1:
        st.metric("게시물", total_posts)
    with col_stat2:
        st.metric("받은 좋아요", total_likes_received)
    with col_stat3:
        st.metric("받은 리포스트", total_reposts_received)
    with col_stat4:
        st.metric("팔로워", follower_count)
    with col_stat5:
        st.metric("팔로잉", following_count)

    st.write("---")

    if is_my_profile:     
        # 프로필 편집 섹션
        with st.expander("프로필 편집", expanded=False):
            # 프로필 이모지 선택
            st.write("**프로필 이모지 선택:**")
            
            # 이모지를 그리드 형태로 표시
            emoji_cols = st.columns(10)  # 10개씩 한 줄에 표시
            
            for i, emoji in enumerate(auth_manager.profile_emojis):
                col_idx = i % 10
                with emoji_cols[col_idx]:
                    if st.button(emoji, key=f"emoji_{i}"):
                        success, message = auth_manager.update_profile_emoji(username, emoji)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            st.write("---")
            
            # 비밀번호 변경
            st.write("**비밀번호 변경:**")
            new_password = st.text_input("새 비밀번호", type="password", key="new_password")
            confirm_password = st.text_input("비밀번호 확인", type="password", key="confirm_password")
            
            if st.button("비밀번호 변경"):
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        # 비밀번호 업데이트
                        auth_manager.df.loc[auth_manager.df['username'] == username, 'password'] = new_password
                        auth_manager.save_users()
                        st.success("비밀번호가 변경되었습니다!")
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.error("새 비밀번호를 입력해주세요.")

def my_posts_page(post_manager, username, auth_manager=None):
    """내 게시물 페이지"""
    st.title("📝 내 게시물")
    
    # 내 게시물 조회
    my_posts = post_manager.posts_df[post_manager.posts_df['username'] == username]
    my_posts = my_posts.sort_values('created_at', ascending=False)
    
    if len(my_posts) == 0:
        st.write("아직 작성한 게시물이 없습니다.")
        st.write("홈에서 첫 번째 게시물을 작성해보세요! 🎉")
        return
    
    # 통계 정보
    total_posts = len(my_posts)
    total_likes = my_posts['like_count'].sum()
    total_reposts = my_posts['repost_count'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 게시물", total_posts)
    with col2:
        st.metric("총 좋아요", total_likes)
    with col3:
        st.metric("총 리포스트", total_reposts)
    
    st.write("---")
    
    # 게시물 목록 (삭제 기능 포함)
    for _, post in my_posts.iterrows():
        display_my_post_with_delete(post.to_dict(), post_manager, username, auth_manager)

def liked_posts_page(post_manager, username, auth_manager=None):
    """좋아요한 게시물 페이지"""
    st.title("❤️ 좋아요한 게시물")
    
    # 사용자가 좋아요한 게시물 ID들 조회
    user_likes = post_manager.likes_df[post_manager.likes_df['username'] == username]
    user_likes = user_likes.sort_values('created_at', ascending=False)
    
    if len(user_likes) == 0:
        st.write("아직 좋아요한 게시물이 없습니다.")
        st.write("홈에서 마음에 드는 게시물에 좋아요를 눌러보세요! ❤️")
        return
    
    st.write(f"총 {len(user_likes)}개의 게시물에 좋아요를 눌렀습니다.")
    st.write("---")
    
    # 좋아요한 게시물들 표시
    for _, like in user_likes.iterrows():
        post_id = like['post_id']
        liked_date = like['created_at']
        
        # 해당 게시물 조회
        post = post_manager.get_post_by_id(post_id)
        if post:
            # 좋아요 누른 날짜 표시
            st.caption(f"좋아요 누른 날짜: {liked_date}")
            
            from enhanced_post_display import display_enhanced_post
            display_enhanced_post(post, post_manager, username, show_actions=True, auth_manager=auth_manager)
        else:
            st.write("*삭제된 게시물입니다.*")
            st.write("---")

def display_my_post_with_delete(post, post_manager, username, auth_manager=None):
    """내 게시물 표시 (삭제 기능 포함)"""
    # 게시물 컨테이너에 스타일 적용
    st.markdown("""
    <div style="
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #1e1e1e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    ">
    """, unsafe_allow_html=True)
    
    # 게시물 헤더 (사용자 정보 + 상세보기 + 삭제 버튼)
    col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
    
    with col1:
        # 프로필 이모지 표시
        if auth_manager:
            profile_emoji = auth_manager.get_user_profile_emoji(post['username'])
            st.markdown(f"<div style='font-size: 50px; text-align: center;'>{profile_emoji}</div>", 
                       unsafe_allow_html=True)
        else:
            st.image("https://via.placeholder.com/50", width=50)
    
    with col2:
        st.markdown(f"**{post['username']}** · {post['created_at']}")
    
    with col3:
        # 상세보기 버튼
        if st.button("📄", key=f"my_detail_{post['post_id']}", help="게시물 상세보기"):
            st.session_state.current_page = 'post_detail'
            st.session_state.selected_post_id = post['post_id']
            st.rerun()
    
    with col4:
        # 삭제 버튼
        if st.button("🗑️", key=f"delete_btn_{post['post_id']}", help="게시물 삭제"):
            st.session_state[f"confirm_delete_{post['post_id']}"] = True
            st.rerun()
    
    # 삭제 확인 대화상자
    if st.session_state.get(f"confirm_delete_{post['post_id']}", False):
        st.markdown("""
        <div style="
            border: 1px solid #ff6b6b;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            background-color: #2a1f1f;
        ">
        """, unsafe_allow_html=True)
        st.warning("⚠️ 이 게시물을 정말 삭제하시겠습니까?")
        st.write("삭제된 게시물은 복구할 수 없습니다.")
        
        col_yes, col_no = st.columns(2)
        
        with col_yes:
            if st.button("삭제", key=f"confirm_yes_{post['post_id']}", type="primary"):
                success, message = post_manager.delete_post(post['post_id'], username)
                if success:
                    st.success(message)
                    st.session_state[f"confirm_delete_{post['post_id']}"] = False
                    st.rerun()
                else:
                    st.error(message)
        
        with col_no:
            if st.button("취소", key=f"confirm_no_{post['post_id']}"):
                st.session_state[f"confirm_delete_{post['post_id']}"] = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 게시물 내용 표시 (간단히)
    if post.get('content'):
        st.write(post['content'])
    
    # 통계 정보
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.write(f"❤️ {post['like_count']} 좋아요")
    with col_stats2:
        st.write(f"🔄 {post['repost_count']} 리포스트")
    with col_stats3:
        # 게시물 타입 표시
        if post['is_repost']:
            st.write("🔄 리포스트")
        else:
            st.write("📝 원본 게시물")
    
    # 게시물 박스 닫기
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def all_users_page(auth_manager, post_manager, follow_manager):
    """모든 사용자를 보여주는 페이지"""
    st.title("🔍 모든 사용자")
    
    current_user_id = auth_manager.get_user_id(st.session_state.username)
    all_users = auth_manager.df[auth_manager.df['id'] != current_user_id]
    
    if len(all_users) == 0:
        st.write("아직 다른 사용자가 없습니다.")
        return
        
    for _, user in all_users.iterrows():
        col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
        
        with col1:
            st.markdown(f"<div style='font-size: 50px; text-align: center;'>{user['profile_emoji']}</div>", 
                       unsafe_allow_html=True)
                       
        with col2:
            st.subheader(f"@{user['username']}")
            # 통계 정보
            follower_count = follow_manager.get_follower_count(user['id'])
            st.caption(f"팔로워: {follower_count}")
        
        with col3:
            # 프로필 보기 버튼
            if st.button("프로필 보기", key=f"view_profile_{user['id']}"):
                st.session_state.current_page = 'view_profile'
                st.session_state.target_user_id = user['id']
                st.rerun()

        with col4:
            # 팔로우/언팔로우 버튼
            if follow_manager.is_following(current_user_id, user['id']):
                if st.button("언팔로우", key=f"unfollow_list_{user['id']}"):
                    success, message = follow_manager.unfollow_user(current_user_id, user['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                if st.button("팔로우", key=f"follow_list_{user['id']}", type="primary"):
                    success, message = follow_manager.follow_user(current_user_id, user['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    st.write("---")