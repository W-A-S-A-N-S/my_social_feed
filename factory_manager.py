# factory_manager.py - 팩토리 관리 모듈
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import streamlit as st
from sim_factory import Sim_Factory

class FactoryManager:
    def __init__(self, factories_file='factories.csv', factory_posts_file='factory_posts.csv'):
        self.factories_file = factories_file
        self.factory_posts_file = factory_posts_file
        self.factories_df = self.load_factories()
        self.factory_posts_df = self.load_factory_posts()
        self.factories = {}
        
        # 기존 팩토리 인스턴스 생성
        self.initialize_factories()
    
    def load_factories(self):
        """팩토리 데이터 로드"""
        try:
            return pd.read_csv(self.factories_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                'factory_id', 'factory_name', 'location', 'created_at', 
                'last_temp', 'last_pressure', 'last_rpm', 'last_product_count', 
                'last_status', 'last_update'
            ])
    
    def load_factory_posts(self):
        """팩토리 포스트 데이터 로드"""
        try:
            return pd.read_csv(self.factory_posts_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                'post_id', 'factory_id', 'factory_name', 'message', 'status_data',
                'priority', 'created_at'
            ])
    
    def save_factories(self):
        """팩토리 데이터 저장"""
        self.factories_df.to_csv(self.factories_file, index=False)
    
    def save_factory_posts(self):
        """팩토리 포스트 저장"""
        self.factory_posts_df.to_csv(self.factory_posts_file, index=False)
    
    def initialize_factories(self):
        """저장된 팩토리들을 인스턴스로 초기화"""
        for _, factory_data in self.factories_df.iterrows():
            factory = Sim_Factory(factory_data['factory_name'])
            factory.factory_id = factory_data['factory_id']
            factory.location = factory_data['location']
            
            # 마지막 상태 복원
            if pd.notna(factory_data['last_temp']):
                factory.temp = factory_data['last_temp']
                factory.pressure = factory_data['last_pressure']
                factory.rpm = factory_data['last_rpm']
                factory.count = factory_data['last_product_count']
                factory.status = factory_data['last_status']
            
            self.factories[factory_data['factory_id']] = factory
    
    def add_factory(self, factory_name, location):
        """새 팩토리 추가"""
        factory_id = f"factory_{len(self.factories_df) + 1:03d}"
        
        # 새 팩토리 인스턴스 생성
        factory = Sim_Factory(factory_name)
        factory.factory_id = factory_id
        factory.location = location
        factory.generate_normal_data()
        
        # 데이터프레임에 추가
        new_factory = {
            'factory_id': factory_id,
            'factory_name': factory_name,
            'location': location,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_temp': factory.temp,
            'last_pressure': factory.pressure,
            'last_rpm': factory.rpm,
            'last_product_count': factory.count,
            'last_status': factory.status,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.factories_df = pd.concat([self.factories_df, pd.DataFrame([new_factory])], ignore_index=True)
        self.factories[factory_id] = factory
        self.save_factories()
        
        # 팩토리 생성 포스트 추가
        self.create_factory_post(factory_id, f"🏭 새로운 팩토리 '{factory_name}'가 {location}에 설립되었습니다!", "normal")
        
        return factory_id
    
    def update_factory_status(self, factory_id, force_abnormal=False):
        """팩토리 상태 업데이트"""
        if factory_id not in self.factories:
            return None
        
        factory = self.factories[factory_id]
        
        # 상태 업데이트
        if force_abnormal or random.random() < 0.15:  # 15% 확률로 비정상
            factory.abnormal_data()
        else:
            factory.generate_normal_data()
        
        # 데이터프레임 업데이트
        factory_idx = self.factories_df[self.factories_df['factory_id'] == factory_id].index
        if len(factory_idx) > 0:
            self.factories_df.loc[factory_idx[0], 'last_temp'] = factory.temp
            self.factories_df.loc[factory_idx[0], 'last_pressure'] = factory.pressure
            self.factories_df.loc[factory_idx[0], 'last_rpm'] = factory.rpm
            self.factories_df.loc[factory_idx[0], 'last_product_count'] = factory.count
            self.factories_df.loc[factory_idx[0], 'last_status'] = factory.status
            self.factories_df.loc[factory_idx[0], 'last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save_factories()
        
        # 상태 변화시 포스트 생성
        status = factory.current_status()
        message = self.generate_status_message(factory)
        priority = "high" if factory.status != "normal" else "normal"
        
        self.create_factory_post(factory_id, message, priority, status)
        
        return status
    
    def generate_status_message(self, factory):
        """상태에 따른 메시지 생성"""
        status_emojis = {
            'normal': '✅',
            'overheat': '🔥',
            'low_pressure': '⚠️',
            'rpm_issue': '⚙️'
        }
        
        emoji = status_emojis.get(factory.status, '❓')
        
        if factory.status == 'normal':
            return f"{emoji} {factory.name} 정상 운영 중 (온도: {factory.temp:.1f}°C, 압력: {factory.pressure:.1f}bar)"
        elif factory.status == 'overheat':
            return f"{emoji} {factory.name} 과열 경고! 온도가 {factory.temp:.1f}°C로 상승했습니다"
        elif factory.status == 'low_pressure':
            return f"{emoji} {factory.name} 압력 부족! 현재 압력: {factory.pressure:.1f}bar"
        elif factory.status == 'rpm_issue':
            return f"{emoji} {factory.name} 속도 문제 발생! 현재 RPM: {factory.rpm:.1f}"
        else:
            return f"{emoji} {factory.name} 상태 점검 필요"
    
    def create_factory_post(self, factory_id, message, priority="normal", status_data=None):
        """팩토리 포스트 생성"""
        factory = self.factories.get(factory_id)
        if not factory:
            return
        
        post_id = len(self.factory_posts_df) + 1
        
        new_post = {
            'post_id': post_id,
            'factory_id': factory_id,
            'factory_name': factory.name,
            'message': message,
            'status_data': json.dumps(status_data, default=str) if status_data else None,
            'priority': priority,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.factory_posts_df = pd.concat([self.factory_posts_df, pd.DataFrame([new_post])], ignore_index=True)
        self.save_factory_posts()
        
        return post_id
    
    def get_factory_feed(self, limit=10):
        """팩토리 피드 조회"""
        return self.factory_posts_df.sort_values('created_at', ascending=False).head(limit)
    
    def get_factory_summary(self):
        """팩토리 요약 정보"""
        total_factories = len(self.factories)
        normal_count = sum(1 for f in self.factories.values() if f.status == 'normal')
        warning_count = sum(1 for f in self.factories.values() if f.status in ['low_pressure', 'rpm_issue'])
        error_count = sum(1 for f in self.factories.values() if f.status == 'overheat')
        
        return {
            'total_factories': total_factories,
            'normal_count': normal_count,
            'warning_count': warning_count,
            'error_count': error_count,
            'factories': [f.current_status() for f in self.factories.values()]
        }
    
    def get_factory_by_id(self, factory_id):
        """팩토리 ID로 조회"""
        return self.factories.get(factory_id)