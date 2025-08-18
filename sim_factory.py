import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class Sim_Factory:
    def __init__(self, name):
        self.name = name
        self.base_temp = 180  # 기본 온도 (°C)
        self.base_pressure = 150  # 기본 압력 (bar)
        self.base_rpm = 50  # 기본 속도 (rpm)
        self.base_product = 100 # 시간당 생산량
        self.status = 'normal'
        
        # 인스턴스 변수로 초기화
        self.temp = self.base_temp
        self.pressure = self.base_pressure
        self.rpm = self.base_rpm
        self.count = self.base_product
    
    def generate_normal_data(self):
        """정상 운영 데이터 생성"""
        self.temp = self.base_temp + random.uniform(-5, 5)
        self.pressure = self.base_pressure + random.uniform(-5, 5)
        self.rpm = self.base_rpm + random.uniform(-2, 2)
        self.count = self.base_product + random.uniform(-5, 5)
        self.status = 'normal'

    def abnormal_data(self):
        """비정상 데이터 생성"""
        abnormal_type = random.choice(['overheat', 'low_pressure', 'rpm_issue'])

        if abnormal_type == 'overheat':
            self.temp = self.temp + random.uniform(30, 60)
            self.status = 'overheat'
        elif abnormal_type == 'low_pressure':
            self.pressure = self.pressure - random.uniform(15, 30)  # 범위 수정
            self.status = 'low_pressure'
        elif abnormal_type == 'rpm_issue':
            self.rpm = self.rpm - random.uniform(15, 25)  # 범위 수정
            self.status = 'rpm_issue'

    def current_status(self):
        """현재 상태 출력"""
        return {
            'timestamp': datetime.now(),  # 함수 호출 수정
            'factory_name': self.name,
            'temperature': round(self.temp, 2),
            'pressure': round(self.pressure, 2),
            'rpm': round(self.rpm, 2),
            'product_count': round(self.count, 2),
            'status': self.status        
        }
