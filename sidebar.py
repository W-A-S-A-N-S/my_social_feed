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
        "❤️ 좋아요한 게시물": "liked_posts"
    }
    
    current_page = st.session_state.get('current_page', 'home')
    
    for label, page_key in menu_options.items():
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{page_key}"):
            st.session_state.current_page = page_key
            st.rerun()
    
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

def profile_page(auth_manager, post_manager, username):
    """프로필 페이지"""
    st.title("👤 프로필")
    
    # 사용자 정보
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.image("https://via.placeholder.com/150", width=150)
    
    with col2:
        st.subheader(f"@{username}")
        
        # 통계 정보
        user_posts = post_manager.posts_df[post_manager.posts_df['username'] == username]
        total_posts = len(user_posts)
        total_likes_received = user_posts['like_count'].sum()
        total_reposts_received = user_posts['repost_count'].sum()
        
        # 사용자가 받은 좋아요 수
        user_likes_given = len(post_manager.likes_df[post_manager.likes_df['username'] == username])
        
        # 가입일 정보
        user_info = auth_manager.df[auth_manager.df['username'] == username]
        if len(user_info) > 0:
            joined_date = user_info['created_at'].iloc[0]
            st.write(f"📅 가입일: {joined_date}")
        
        # 통계 표시
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("게시물", total_posts)
        with col_stat2:
            st.metric("받은 좋아요", total_likes_received)
        with col_stat3:
            st.metric("받은 리포스트", total_reposts_received)
    
    st.write("---")
    
    # 프로필 편집 섹션
    with st.expander("프로필 편집", expanded=False):
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

def my_posts_page(post_manager, username):
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
        display_my_post_with_delete(post.to_dict(), post_manager, username)

def liked_posts_page(post_manager, username):
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
            display_post(post, post_manager, username, show_actions=True)
        else:
            st.write("*삭제된 게시물입니다.*")
            st.write("---")

def display_my_post_with_delete(post, post_manager, username):
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
    
    # 게시물 내용 표시
    # 리포스트인 경우
    if post['is_repost'] and post['original_post_id']:
        if post['content']:  # 코멘트가 있는 경우
            st.write(post['content'])
            st.markdown("---")
        
        # 원본 게시물 표시 (중첩된 박스 스타일)
        original_post = post_manager.get_post_by_id(post['original_post_id'])
        if original_post:
            st.markdown("🔄 **리포스트된 게시물:**")
            st.markdown("""
            <div style="
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px;
                margin: 10px 0;
                background-color: #2a2a2a;
            ">
            """, unsafe_allow_html=True)
            st.markdown(f"**{original_post['username']}** · {original_post['created_at']}")
            st.write(original_post['content'])
            
            # 원본 게시물의 이미지 표시
            if original_post.get('has_image') and original_post.get('image_path'):
                original_image_path = original_post.get('image_path')
                if original_image_path and isinstance(original_image_path, str) and os.path.exists(original_image_path):
                    st.image(original_image_path, width=400)
                else:
                    st.write("*이미지를 불러올 수 없습니다.*")
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.write("*삭제된 게시물입니다.*")
    else:
        # 일반 게시물
        st.write(post['content'])
        
        # 이미지 표시
        if post.get('has_image') and post.get('image_path'):
            image_path = post.get('image_path')
            if image_path and isinstance(image_path, str) and os.path.exists(image_path):
                st.image(image_path, width=400)
            else:
                st.write("*이미지를 불러올 수 없습니다.*")
    
    # 통계 정보 (액션 버튼 없이)
    st.markdown("<br>", unsafe_allow_html=True)  # 여백 추가
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
    
    # 게시물 박스 닫기 (맨 마지막에!)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)  # 게시물 간 여백

def get_user_stats(post_manager, auth_manager, username):
    """사용자 통계 정보 조회"""
    user_posts = post_manager.posts_df[post_manager.posts_df['username'] == username]
    user_likes = post_manager.likes_df[post_manager.likes_df['username'] == username]
    
    # 가입일
    user_info = auth_manager.df[auth_manager.df['username'] == username]
    joined_date = user_info['created_at'].iloc[0] if len(user_info) > 0 else "알 수 없음"
    
    stats = {
        'total_posts': len(user_posts),
        'total_likes_received': user_posts['like_count'].sum(),
        'total_reposts_received': user_posts['repost_count'].sum(),
        'total_likes_given': len(user_likes),
        'joined_date': joined_date
    }
    
    return stats