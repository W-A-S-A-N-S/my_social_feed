import pandas as pd
import streamlit as st
from datetime import datetime
import json
import os
from PIL import Image
import io
from auth import AuthManager # 👈 AuthManager import 추가

class PostManager:
    def __init__(self, posts_file='posts.csv', likes_file='likes.csv', images_dir='post_images'):
        self.posts_file = posts_file
        self.likes_file = likes_file
        self.images_dir = images_dir
        self.posts_df = self.load_posts()
        self.likes_df = self.load_likes()
        
        # 이미지 저장 디렉토리 생성
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
    
    def load_posts(self):
        """게시물 데이터 로드"""
        try:
            df = pd.read_csv(self.posts_file)
            
            # 기존 데이터에 이미지 관련 컬럼이 없으면 추가
            if 'has_image' not in df.columns:
                df['has_image'] = False
            if 'image_path' not in df.columns:
                df['image_path'] = None
            
            # 데이터 타입 정리 - 경고 없는 방법 사용
            df['image_path'] = df['image_path'].where(df['image_path'].notna(), None)
            # fillna 대신 직접 None 값을 False로 변경
            df.loc[df['has_image'].isna(), 'has_image'] = False
                
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                'post_id', 'username', 'content', 'created_at', 
                'is_repost', 'original_post_id', 'like_count', 'repost_count',
                'has_image', 'image_path'
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
    
    def save_image(self, uploaded_file, post_id):
        """업로드된 이미지 저장"""
        try:
            # 파일 확장자 확인
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                return None, "지원하지 않는 이미지 형식입니다."
            
            # 이미지 파일명 생성
            image_filename = f"post_{post_id}.{file_extension}"
            image_path = os.path.join(self.images_dir, image_filename)
            
            # 이미지 크기 조정 및 저장
            image = Image.open(uploaded_file)
            
            # 이미지 크기 제한 (최대 800x600)
            max_size = (800, 600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 이미지 저장
            image.save(image_path, optimize=True, quality=85)
            
            return image_path, "이미지가 저장되었습니다."
            
        except Exception as e:
            return None, f"이미지 저장 중 오류가 발생했습니다: {str(e)}"
    
    def create_post(self, username, content, uploaded_image=None):
        """새 게시물 작성"""
        if not content.strip() and not uploaded_image:
            return False, "내용 또는 이미지를 추가해주세요!"
        
        post_id = self.get_next_post_id()
        image_path = None
        has_image = False
        
        # 이미지 처리
        if uploaded_image is not None:
            image_path, image_message = self.save_image(uploaded_image, post_id)
            if image_path:
                has_image = True
            else:
                return False, image_message
        
        new_post = {
            'post_id': post_id,
            'username': username,
            'content': content.strip(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_repost': False,
            'original_post_id': None,
            'like_count': 0,
            'repost_count': 0,
            'has_image': has_image,
            'image_path': image_path if has_image else None
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
            'repost_count': 0,
            'has_image': False,
            'image_path': None
        }
        
        self.posts_df = pd.concat([self.posts_df, pd.DataFrame([new_repost])], ignore_index=True)
        
        # 원본 게시물의 리포스트 카운트 증가
        self.posts_df.loc[self.posts_df['post_id'] == original_post_id, 'repost_count'] += 1
        self.save_posts()
        
        return True, "리포스트되었습니다!"
    
    def delete_post(self, post_id, username):
        """게시물 삭제 (본인 게시물만)"""
        # 게시물 존재 및 소유권 확인
        post = self.get_post_by_id(post_id)
        if not post:
            return False, "게시물을 찾을 수 없습니다."
        
        if post['username'] != username:
            return False, "본인의 게시물만 삭제할 수 있습니다."
        
        # 이미지 파일 삭제
        if post.get('has_image') and post.get('image_path'):
            try:
                if os.path.exists(post['image_path']):
                    os.remove(post['image_path'])
            except Exception as e:
                print(f"이미지 삭제 중 오류: {e}")
        
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


def display_profile_emoji(auth_manager, username, size=50):
    """프로필 이모지를 표시하는 공통 함수"""
    if auth_manager:
        emoji = auth_manager.get_user_profile_emoji(username)
        st.markdown(
            f"<div style='font-size: {size}px; text-align: center;'>{emoji}</div>",
            unsafe_allow_html=True
        )
    else:
        st.image("https://via.placeholder.com/50", width=size)


def create_post_form(post_manager, username):
    """게시물 작성 폼"""
    with st.expander("새 게시물 작성", expanded=False):
        post_content = st.text_area("무슨 일이 일어나고 있나요?", height=100, key="new_post_content")
        
        # 이미지 업로드
        uploaded_image = st.file_uploader(
            "이미지 업로드 (선택사항)", 
            type=['jpg', 'jpeg', 'png', 'gif', 'webp'],
            key="post_image_upload"
        )
        
        # 업로드된 이미지 미리보기
        if uploaded_image is not None:
            st.write("**이미지 미리보기:**")
            image = Image.open(uploaded_image)
            st.image(image, width=300)
        
        if st.button("게시하기", key="create_post_btn"):
            success, message = post_manager.create_post(username, post_content, uploaded_image)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def display_post(post, post_manager, current_username, show_actions=True, auth_manager=None):
    """개별 게시물 표시"""
    with st.container():
        # 게시물 정보
        col1, col2, col3 = st.columns([1, 5, 1])
        
        with col1:
            # 프로필 이모지 표시 (auth_manager가 있을 때)
            display_profile_emoji(auth_manager, post['username'], size=50)
        
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
                    st.markdown(f"**{original_post['username']}** · {original_post['created_at']}")
                    st.write(original_post['content'])
                    
                    # 원본 게시물의 이미지 표시
                    if original_post.get('has_image') and original_post.get('image_path'):
                        original_image_path = original_post.get('image_path')
                        if original_image_path and isinstance(original_image_path, str) and os.path.exists(original_image_path):
                            st.image(original_image_path, width=400)
                        else:
                            st.write("*이미지를 불러올 수 없습니다.*")
                else:
                    st.write("*삭제된 게시물입니다.*")
            else:
                # 일반 게시물
                st.write(post['content'])
                
                # 이미지 표시
                if post.get('has_image') and post.get('image_path'):
                    # image_path가 문자열이고 유효한 경로인지 확인
                    image_path = post.get('image_path')
                    if image_path and isinstance(image_path, str) and os.path.exists(image_path):
                        st.image(image_path, width=400)
                    else:
                        st.write("*이미지를 불러올 수 없습니다.*")
        
        with col3:
            # 개별 게시물 페이지로 이동 버튼
            if st.button("📄", key=f"detail_{post['post_id']}", help="게시물 상세보기"):
                st.session_state.current_page = 'post_detail'
                st.session_state.selected_post_id = post['post_id']
                st.rerun()
        
        # 액션 버튼들
        if show_actions:
            col_like, col_repost, col_stats = st.columns([1, 1, 4])
            
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
        
        st.write("---")

def post_detail_page(post_manager, current_username, auth_manager=None):
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
            #프로필 이모지 표시
            display_profile_emoji(auth_manager, post['username'], size=50)
        
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
                    st.markdown(f"**{original_post['username']}** · {original_post['created_at']}")
                    st.write(original_post['content'])
                    
                    # 원본 게시물의 이미지 표시
                    if original_post.get('has_image') and original_post.get('image_path'):
                        original_image_path = original_post.get('image_path')
                        if original_image_path and isinstance(original_image_path, str) and os.path.exists(original_image_path):
                            st.image(original_image_path, width=500)
                        else:
                            st.write("*이미지를 불러올 수 없습니다.*")
                else:
                    st.write("*삭제된 게시물입니다.*")
            else:
                st.markdown("**내용:**")
                st.write(post['content'])
                
                # 이미지 표시 (상세 페이지에서는 더 크게)
                if post.get('has_image') and post.get('image_path'):
                    st.markdown("**첨부 이미지:**")
                    image_path = post.get('image_path')
                    if image_path and isinstance(image_path, str) and os.path.exists(image_path):
                        st.image(image_path, width=600)
                    else:
                        st.write("*이미지를 불러올 수 없습니다.*")
    
    st.write("---")
    
    # 상호작용 통계
    st.subheader("통계")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("좋아요", post['like_count'])
    with col2:
        st.metric("리포스트", post['repost_count'])
    with col3:
        post_type = "리포스트" if post['is_repost'] else "원본 게시물"
        st.metric("유형", post_type)
    with col4:
        has_image_text = "있음" if post.get('has_image') else "없음"
        st.metric("이미지", has_image_text)
    
    # 좋아요 누른 사용자 목록
    st.subheader("좋아요 누른 사용자")
    likes = post_manager.get_post_likes(post_id)
    
    if len(likes) > 0:
        for _, like in likes.iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                # 좋아요 누른 사람 프로필 이모지 표시
                display_profile_emoji(auth_manager, like['username'], size=40)
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

def display_posts_feed(post_manager, current_username, auth_manager=None):
    """게시물 피드 표시"""
    st.subheader("최신 게시물")
    
    posts = post_manager.get_posts_feed()
    
    if len(posts) == 0:
        st.write("아직 게시물이 없습니다. 첫 번째 게시물을 작성해보세요!")
        return
    
    for _, post in posts.iterrows():
        display_post(post.to_dict(), post_manager, current_username, show_actions=True, auth_manager=auth_manager)


def display_profile_emoji(auth_manager, username, size=50):
    """프로필 이모지를 표시하는 공통 함수"""
    if auth_manager:
        emoji = auth_manager.get_user_profile_emoji(username)
        st.markdown(
            f"<div style='font-size: {size}px; text-align: center;'>{emoji}</div>",
            unsafe_allow_html=True
        )
    else:
        st.image("https://via.placeholder.com/50", width=size)