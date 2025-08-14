# follow.py
import pandas as pd

class FollowManager:
    def __init__(self, followers_file='followers.csv'):
        self.followers_file = followers_file
        self.df = self.load_followers()

    def load_followers(self):
        """팔로워 데이터 로드"""
        try:
            return pd.read_csv(self.followers_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=['follower_id', 'followed_id'])

    def save_followers(self):
        """팔로워 데이터 저장"""
        self.df.to_csv(self.followers_file, index=False)

    def is_following(self, follower_id, followed_id):
        """현재 사용자가 특정 사용자를 팔로우하는지 확인"""
        if self.df.empty:
            return False
        return len(self.df[
            (self.df['follower_id'] == follower_id) & (self.df['followed_id'] == followed_id)
        ]) > 0

    def follow_user(self, follower_id, followed_id):
        """특정 사용자를 팔로우"""
        if self.is_following(follower_id, followed_id):
            return False, "이미 팔로우 중입니다."
        
        new_follow = {
            'follower_id': follower_id,
            'followed_id': followed_id
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_follow])], ignore_index=True)
        self.save_followers()
        return True, "팔로우했습니다."

    def unfollow_user(self, follower_id, followed_id):
        """특정 사용자를 언팔로우"""
        if not self.is_following(follower_id, followed_id):
            return False, "팔로우하고 있지 않습니다."
        
        self.df = self.df[
            ~((self.df['follower_id'] == follower_id) & (self.df['followed_id'] == followed_id))
        ]
        self.save_followers()
        return True, "언팔로우했습니다."

    def get_follower_count(self, user_id):
        """특정 사용자의 팔로워 수 조회"""
        return len(self.df[self.df['followed_id'] == user_id])

    def get_following_count(self, user_id):
        """특정 사용자가 팔로우하는 사람 수 조회"""
        return len(self.df[self.df['follower_id'] == user_id])