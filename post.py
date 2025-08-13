import pandas as pd
import streamlit as st
from datetime import datetime
import json

class PostManager:
    def __init__(self, posts_file='posts.csv', likes_file='likes.csv'):
        self.posts_file = posts_file
        self.likes_file = likes_file
        self.posts_df = self.load_posts()
        self.likes_df = self.load_likes()
    
    def load_posts(self):
        """게시물 데이터 로드"""
        try:
            return pd.read_csv(self.posts_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                'post_id', 'username', 'content', 'created_at', 
                'is_repost', 'original_post_id', 'like_count', 'repost_count'
            ])
    
    def load_likes(self):
        """좋아요 데이터 로드"""
        try:
            return pd.read_csv(self.likes_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=['like_id', 'post_id', 'username', 'created_at'])
    
    def save_posts(self):
        """게시물 데이터 저장"""
        self.posts_df.to_csv(self.posts_file, index=False)
    
    def save_likes(self):
        """좋아요 데이터 저장"""
        self.likes_df.to_csv(self.likes_file, index=False)
    
    def get_next_post_id(self):
        """새로운 게시물 ID 생성"""
        if len(self.posts_df) == 0:
            return 1
        else:
            return self.posts_df['post_id'].max() + 1
    
    def get_next_like_id(self):
        """새로운 좋아요 ID 생성"""
        if len(self.likes_df) == 0:
            return 1
        else:
            return self.likes_df['like_id'].max() + 1
    
    def create_post(self, username, content):
        """새 게시물 작성"""
        if not content.strip():
            return False, "내용을 입력해주세요!"
        
        new_post = {
            'post_id': self.get_next_post_id(),
            'username': username,
            'content': content.strip(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_repost': False,
            'original_post_id': None,
            'like_count': 0,
            'repost_count': 0
        }
        
        self.posts_df = pd.concat([self.posts_df, pd.DataFrame([new_post])], ignore_index=True)
        self.save_posts()
        
        return True, "게시물이 작성되었습니다!"
    
    def create_repost(self, username, original_post_id, comment=""):
        """리포스트 작성"""
        # 원본 게시물 확인
        original_post = self.get_post_by_id(original_post_id)
        if original_post is None:
            return False, "원본 게시물을 찾을 수 없습니다."
        
        new_repost = {
            'post_id': self.get_next_post_id(),
            'username': username,
            'content': comment.strip() if comment else "",
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_repost': True,
            'original_post_id': original_post_id,
            'like_count': 0,
            'repost_count': 0
        }
        
        self.posts_df = pd.concat([self.posts_df, pd.DataFrame([new_repost])], ignore_index=True)
        
        # 원본 게시물의 리포스트 카운트 증가
        self.posts_df.loc[self.posts_df['post_id'] == original_post_id, 'repost_count'] += 1
        self.save_posts()
        
        return True, "리포스트되었습니다!"
    
    def toggle_like(self, post_id, username):
        """좋아요 토글 (좋아요 추가/제거)"""
        # 이미 좋아요를 눌렀는지 확인
        existing_like = self.likes_df[
            (self.likes_df['post_id'] == post_id) & 
            (self.likes_df['username'] == username)
        ]
        
        if len(existing_like) > 0:
            # 좋아요 제거
            self.likes_df = self.likes_df[
                ~((self.likes_df['post_id'] == post_id) & 
                  (self.likes_df['username'] == username))
            ]
            # 게시물의 좋아요 카운트 감소
            self.posts_df.loc[self.posts_df['post_id'] == post_id, 'like_count'] -= 1
            action = "removed"
        else:
            # 좋아요 추가
            new_like = {
                'like_id': self.get_next_like_id(),
                'post_id': post_id,
                'username': username,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.likes_df = pd.concat([self.likes_df, pd.DataFrame([new_like])], ignore_index=True)
            # 게시물의 좋아요 카운트 증가
            self.posts_df.loc[self.posts_df['post_id'] == post_id, 'like_count'] += 1
            action = "added"
        
        self.save_likes()
        self.save_posts()
        
        return action
    
    def delete_post(self, post_id, username):
        """게시물 삭제 (본인 게시물만)"""
        # 게시물 존재 및 소유권 확인
        post = self.get_post_by_id(post_id)
        if not post:
            return False, "게시물을 찾을 수 없습니다."
        
        if post['username'] != username:
            return False, "본인의 게시물만 삭제할 수 있습니다."
        
        # 게시물 삭제
        self.posts_df = self.posts_df[self.posts_df['post_id'] != post_id]
        
        # 해당 게시물의 좋아요 데이터도 삭제
        self.likes_df = self.likes_df[self.likes_df['post_id'] != post_id]
        
        # 만약 이 게시물이 원본이고 리포스트된 게시물들이 있다면, 
        # 리포스트 게시물들의 original_post_id를 None으로 설정 (삭제된 게시물 표시용)
        self.posts_df.loc[self.posts_df['original_post_id'] == post_id, 'original_post_id'] = None
        
        self.save_posts()
        self.save_likes()
        
        return True, "게시물이 삭제되었습니다."
    
    def get_post_by_id(self, post_id):
        """게시물 ID로 게시물 조회"""
        post = self.posts_df[self.posts_df['post_id'] == post_id]
        if len(post) > 0:
            return post.iloc[0].to_dict()
        return None
    
    def get_posts_feed(self, limit=10):
        """피드용 게시물 조회 (최신순)"""
        return self.posts_df.sort_values('created_at', ascending=False).head(limit)
    
    def user_liked_post(self, post_id, username):
        """사용자가 해당 게시물에 좋아요를 눌렀는지 확인"""
        return len(self.likes_df[
            (self.likes_df['post_id'] == post_id) & 
            (self.likes_df['username'] == username)
        ]) > 0
    
    def get_post_likes(self, post_id):
        """게시물의 좋아요 목록 조회"""
        return self.likes_df[self.likes_df['post_id'] == post_id].sort_values('created_at', ascending=False)

def create_post_form(post_manager, username):
    """게시물 작성 폼"""
    with st.expander("새 게시물 작성", expanded=False):
        post_content = st.text_area("무슨 일이 일어나고 있나요?", height=100, key="new_post_content")
        
        if st.button("게시하기", key="create_post_btn"):
            success, message = post_manager.create_post(username, post_content)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def display_post(post, post_manager, current_username, show_actions=True):
    """개별 게시물 표시"""
    # Streamlit 네이티브 컨테이너 사용
    with st.container():
        # CSS 스타일 적용
        st.markdown("""
        <style>
        .post-container {
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background-color: #1e1e1e;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 컨테이너에 CSS 클래스 적용
        with st.container():
            st.markdown('<div class="post-container">', unsafe_allow_html=True)
            
            # 사용자 정보와 게시물 링크
            col1, col2, col3 = st.columns([1, 5, 1])
            with col1:
                st.image("https://via.placeholder.com/50", width=50)
            with col2:
                st.markdown(f"**{post['username']}** · {post['created_at']}")
                
                # 리포스트인 경우
                if post['is_repost'] and post['original_post_id']:
                    if post['content']:  # 코멘트가 있는 경우
                        st.write(post['content'])
                        st.markdown("---")
                    
                    # 원본 게시물 표시
                    original_post = post_manager.get_post_by_id(post['original_post_id'])
                    if original_post:
                        st.markdown("🔄 **리포스트된 게시물:**")
                        with st.container():
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
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.write("*삭제된 게시물입니다.*")
                else:
                    # 일반 게시물
                    st.write(post['content'])
            
            with col3:
                # 개별 게시물 페이지로 이동 버튼
                if st.button("📄", key=f"detail_{post['post_id']}", help="게시물 상세보기"):
                    st.session_state.current_page = 'post_detail'
                    st.session_state.selected_post_id = post['post_id']
                    st.rerun()
                
                # 액션 버튼들
                if show_actions:
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_like, col_repost = st.columns(2)
                    
                    with col_like:
                        # 좋아요 버튼
                        liked = post_manager.user_liked_post(post['post_id'], current_username)
                        like_emoji = "❤️" if liked else "🤍"
                        if st.button(f"{like_emoji} {post['like_count']}", key=f"like_{post['post_id']}"):
                            post_manager.toggle_like(post['post_id'], current_username)
                            st.rerun()
                    
                    with col_repost:
                        # 리포스트 버튼
                        if st.button(f"🔄 {post['repost_count']}", key=f"repost_{post['post_id']}"):
                            st.session_state[f"show_repost_{post['post_id']}"] = True
                            st.rerun()
                    
                    # 리포스트 폼
                    if st.session_state.get(f"show_repost_{post['post_id']}", False):
                        with st.expander("리포스트하기", expanded=True):
                            repost_comment = st.text_area("코멘트 추가 (선택사항)", key=f"repost_comment_{post['post_id']}")
                            col_submit, col_cancel = st.columns(2)
                            
                            with col_submit:
                                if st.button("리포스트", key=f"submit_repost_{post['post_id']}"):
                                    success, message = post_manager.create_repost(
                                        current_username, post['post_id'], repost_comment
                                    )
                                    if success:
                                        st.success(message)
                                        st.session_state[f"show_repost_{post['post_id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(message)
                            
                            with col_cancel:
                                if st.button("취소", key=f"cancel_repost_{post['post_id']}"):
                                    st.session_state[f"show_repost_{post['post_id']}"] = False
                                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)  # 게시물 간 여백

def post_detail_page(post_manager, current_username):
    """개별 게시물 상세 페이지"""
    st.title("📄 게시물 상세")
    
    # 뒤로가기 버튼
    if st.button("← 뒤로가기"):
        st.session_state.current_page = 'home'
        if 'selected_post_id' in st.session_state:
            del st.session_state['selected_post_id']
        st.rerun()
    
    # 선택된 게시물 조회
    post_id = st.session_state.get('selected_post_id')
    if not post_id:
        st.error("게시물을 찾을 수 없습니다.")
        return
    
    post = post_manager.get_post_by_id(post_id)
    if not post:
        st.error("삭제된 게시물입니다.")
        return
    
    st.write("---")
    
    # 게시물 상세 정보 표시
    st.subheader("게시물 정보")
    
    # 큰 게시물 카드
    with st.container():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.image("https://via.placeholder.com/80", width=80)
        
        with col2:
            st.markdown(f"### {post['username']}")
            st.markdown(f"**작성일:** {post['created_at']}")
            
            # 리포스트인 경우
            if post['is_repost'] and post['original_post_id']:
                st.markdown("🔄 **리포스트**")
                if post['content']:
                    st.markdown("**코멘트:**")
                    st.write(post['content'])
                
                st.markdown("---")
                st.markdown("**원본 게시물:**")
                
                original_post = post_manager.get_post_by_id(post['original_post_id'])
                if original_post:
                    with st.container():
                        st.markdown(f"**{original_post['username']}** · {original_post['created_at']}")
                        st.write(original_post['content'])
                else:
                    st.write("*삭제된 게시물입니다.*")
            else:
                st.markdown("**내용:**")
                st.write(post['content'])
    
    st.write("---")
    
    # 상호작용 통계
    st.subheader("통계")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("좋아요", post['like_count'])
    with col2:
        st.metric("리포스트", post['repost_count'])
    with col3:
        post_type = "리포스트" if post['is_repost'] else "원본 게시물"
        st.metric("유형", post_type)
    
    # 좋아요 누른 사용자 목록
    st.subheader("좋아요 누른 사용자")
    likes = post_manager.get_post_likes(post_id)
    
    if len(likes) > 0:
        for _, like in likes.iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image("https://via.placeholder.com/40", width=40)
            with col2:
                st.write(f"**{like['username']}** · {like['created_at']}")
    else:
        st.write("아직 좋아요가 없습니다.")
    
    st.write("---")
    
    # 액션 버튼들 (큰 버튼)
    st.subheader("액션")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        liked = post_manager.user_liked_post(post_id, current_username)
        like_emoji = "❤️" if liked else "🤍"
        if st.button(f"{like_emoji} 좋아요", key="detail_like", use_container_width=True):
            post_manager.toggle_like(post_id, current_username)
            st.rerun()
    
    with col2:
        if st.button("🔄 리포스트", key="detail_repost", use_container_width=True):
            st.session_state.show_detail_repost = True
            st.rerun()
    
    with col3:
        if post['username'] == current_username:
            if st.button("🗑️ 삭제", key="detail_delete", use_container_width=True):
                st.session_state.show_detail_delete = True
                st.rerun()
    
    # 리포스트 폼
    if st.session_state.get('show_detail_repost', False):
        st.subheader("리포스트하기")
        repost_comment = st.text_area("코멘트 추가 (선택사항)", key="detail_repost_comment")
        
        col_submit, col_cancel = st.columns(2)
        with col_submit:
            if st.button("리포스트하기", key="detail_submit_repost"):
                success, message = post_manager.create_repost(current_username, post_id, repost_comment)
                if success:
                    st.success(message)
                    st.session_state.show_detail_repost = False
                    st.rerun()
                else:
                    st.error(message)
        
        with col_cancel:
            if st.button("취소", key="detail_cancel_repost"):
                st.session_state.show_detail_repost = False
                st.rerun()
    
    # 삭제 확인
    if st.session_state.get('show_detail_delete', False):
        st.error("⚠️ 이 게시물을 정말 삭제하시겠습니까?")
        st.write("삭제된 게시물은 복구할 수 없습니다.")
        
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("삭제", key="detail_confirm_delete", type="primary"):
                success, message = post_manager.delete_post(post_id, current_username)
                if success:
                    st.success(message)
                    st.session_state.current_page = 'home'
                    if 'selected_post_id' in st.session_state:
                        del st.session_state['selected_post_id']
                    st.session_state.show_detail_delete = False
                    st.rerun()
                else:
                    st.error(message)
        
        with col_no:
            if st.button("취소", key="detail_cancel_delete"):
                st.session_state.show_detail_delete = False
                st.rerun()

def display_posts_feed(post_manager, current_username):
    """게시물 피드 표시"""
    st.subheader("최신 게시물")
    
    posts = post_manager.get_posts_feed()
    
    if len(posts) == 0:
        st.write("아직 게시물이 없습니다. 첫 번째 게시물을 작성해보세요!")
        return
    
    for _, post in posts.iterrows():
        display_post(post.to_dict(), post_manager, current_username)