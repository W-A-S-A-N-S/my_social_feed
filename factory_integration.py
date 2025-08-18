# factory_integration.py - 기존 시스템과 통합
import json
from post import PostManager

def integrate_factory_with_social_feed(post_manager, factory_manager):
    """팩토리 포스트를 일반 소셜 피드에 통합"""
    
    # 팩토리 포스트를 일반 포스트 형식으로 변환
    factory_posts = factory_manager.get_factory_feed(1)
    
    for _, factory_post in factory_posts.iterrows():
        # 시스템 사용자로 포스트 생성
        system_username = "🏭_Factory_System"
        
        # 포스트 내용 구성
        content = factory_post['message']
        
        # 상태 데이터가 있으면 차트 형태로 추가
        if factory_post['status_data'] and factory_post['status_data'] != 'null':
            try:
                status_data = json.loads(factory_post['status_data'])
                chart_data = {
                    "type": "factory_status",
                    "title": f"{factory_post['factory_name']} 실시간 상태",
                    "data": {
                        "온도": status_data['temperature'],
                        "압력": status_data['pressure'],
                        "RPM": status_data['rpm'],
                        "생산량": status_data['product_count']
                    },
                    "status": status_data['status'],
                    "timestamp": status_data['timestamp'],
                    "factory_id": factory_post['factory_id'],
                    "priority": factory_post['priority']
                }
                content = json.dumps(chart_data)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        
        # 중복 포스트 방지를 위한 체크
        existing_posts = post_manager.posts_df[
            (post_manager.posts_df['username'] == system_username) &
            (post_manager.posts_df['created_at'] == factory_post['created_at'])
        ]
        
        if len(existing_posts) == 0:
            post_manager.create_post(system_username, content)

def create_factory_status_post(factory_manager, factory_id, post_manager):
    """특정 팩토리의 현재 상태를 소셜 포스트로 생성"""
    factory = factory_manager.get_factory_by_id(factory_id)
    if not factory:
        return False, "팩토리를 찾을 수 없습니다."
    
    status = factory.current_status()
    system_username = "🏭_Factory_System"
    
    # 차트 데이터 생성
    chart_data = {
        "type": "factory_status",
        "title": f"{factory.name} 현재 상태",
        "data": {
            "온도": status['temperature'],
            "압력": status['pressure'], 
            "RPM": status['rpm'],
            "생산량": status['product_count']
        },
        "status": status['status'],
        "timestamp": status['timestamp'],
        "factory_id": factory_id,
        "priority": "high" if status['status'] != "normal" else "normal"
    }
    
    content = json.dumps(chart_data)
    success, message = post_manager.create_post(system_username, content)
    
    return success, message

def get_factory_posts_from_social_feed(post_manager):
    """소셜 피드에서 팩토리 관련 포스트만 필터링"""
    system_username = "🏭_Factory_System"
    factory_posts = post_manager.posts_df[
        post_manager.posts_df['username'] == system_username
    ].sort_values('created_at', ascending=False)
    
    return factory_posts

def create_factory_summary_post(factory_manager, post_manager):
    """전체 팩토리 요약 정보를 소셜 포스트로 생성"""
    summary = factory_manager.get_factory_summary()
    system_username = "🏭_Factory_System"
    
    if summary['total_factories'] == 0:
        return False, "등록된 팩토리가 없습니다."
    
    # 요약 메시지 생성
    status_text = f"""
🏭 **팩토리 전체 현황 보고**

📊 **운영 현황**
• 총 팩토리: {summary['total_factories']}개
• ✅ 정상 운영: {summary['normal_count']}개
• ⚠️ 경고 상태: {summary['warning_count']}개  
• 🔥 위험 상태: {summary['error_count']}개

📈 **정상 가동률**: {(summary['normal_count']/summary['total_factories']*100):.1f}%
    """
    
    if summary['error_count'] > 0:
        status_text += "\n🚨 **즉시 점검 필요한 팩토리가 있습니다!**"
    elif summary['warning_count'] > 0:
        status_text += "\n💡 **일부 팩토리에서 주의가 필요합니다.**"
    else:
        status_text += "\n✅ **모든 팩토리가 정상 가동 중입니다.**"
    
    success, message = post_manager.create_post(system_username, status_text.strip())
    return success, message

def create_emergency_alert_post(factory_manager, factory_id, post_manager, alert_type="overheat"):
    """응급 상황 알림 포스트 생성"""
    factory = factory_manager.get_factory_by_id(factory_id)
    if not factory:
        return False, "팩토리를 찾을 수 없습니다."
    
    status = factory.current_status()
    system_username = "🏭_Factory_System"
    
    alert_messages = {
        "overheat": f"🚨 **긴급 알림** 🚨\n\n🔥 {factory.name}에서 과열 상황 발생!\n온도: {status['temperature']:.1f}°C (위험 수준)\n\n즉시 냉각 시스템 점검이 필요합니다.",
        "low_pressure": f"⚠️ **경고 알림** ⚠️\n\n💨 {factory.name}에서 압력 부족 감지!\n압력: {status['pressure']:.1f}bar (기준 미달)\n\n압력 공급 시스템을 확인해주세요.",
        "rpm_issue": f"⚙️ **장비 알림** ⚙️\n\n🔧 {factory.name}에서 속도 이상 감지!\nRPM: {status['rpm']:.1f} (비정상)\n\n구동 시스템 점검이 필요합니다.",
        "maintenance": f"🔧 **정비 알림** 🔧\n\n📋 {factory.name} 정기 점검 시간입니다.\n현재 상태: {status['status']}\n\n예방 정비를 실시해주세요."
    }
    
    alert_content = alert_messages.get(alert_type, f"📢 {factory.name}에서 알림이 발생했습니다.")
    
    # 긴급도에 따른 추가 정보
    if alert_type == "overheat":
        chart_data = {
            "type": "factory_emergency",
            "title": f"🚨 {factory.name} 긴급 상황",
            "alert_type": alert_type,
            "data": {
                "온도": status['temperature'],
                "압력": status['pressure'],
                "RPM": status['rpm'],
                "생산량": status['product_count']
            },
            "status": status['status'],
            "timestamp": status['timestamp'],
            "factory_id": factory_id,
            "priority": "emergency"
        }
        content = json.dumps(chart_data)
    else:
        content = alert_content
    
    success, message = post_manager.create_post(system_username, content)
    return success, message

def schedule_factory_monitoring(factory_manager, post_manager, monitoring_interval=300):
    """팩토리 모니터링 스케줄링 (초 단위)"""
    import threading
    import time
    
    def monitor_factories():
        while True:
            try:
                # 모든 팩토리 상태 체크
                for factory_id in factory_manager.factories.keys():
                    factory = factory_manager.get_factory_by_id(factory_id)
                    if factory:
                        old_status = factory.status
                        
                        # 상태 업데이트
                        new_status_data = factory_manager.update_factory_status(factory_id)
                        
                        # 상태 변화가 있으면 소셜 피드에 포스트
                        if new_status_data and new_status_data['status'] != old_status:
                            if new_status_data['status'] != 'normal':
                                # 비정상 상태면 긴급 알림
                                create_emergency_alert_post(
                                    factory_manager, factory_id, post_manager, 
                                    new_status_data['status']
                                )
                            else:
                                # 정상으로 복구되면 일반 상태 포스트
                                create_factory_status_post(
                                    factory_manager, factory_id, post_manager
                                )
                
                # 전체 요약도 주기적으로 포스트 (1시간마다)
                current_time = time.time()
                if hasattr(monitor_factories, 'last_summary_time'):
                    if current_time - monitor_factories.last_summary_time > 3600:  # 1시간
                        create_factory_summary_post(factory_manager, post_manager)
                        monitor_factories.last_summary_time = current_time
                else:
                    monitor_factories.last_summary_time = current_time
                
                time.sleep(monitoring_interval)
                
            except Exception as e:
                print(f"모니터링 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    # 백그라운드 스레드로 실행
    monitor_thread = threading.Thread(target=monitor_factories, daemon=True)
    monitor_thread.start()
    
    return monitor_thread