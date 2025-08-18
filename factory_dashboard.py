# factory_dashboard.py - 팩토리 대시보드 페이지
import streamlit as st
import json
from factory_integration import integrate_factory_with_social_feed

def factory_dashboard_page(factory_manager, post_manager):
    """팩토리 대시보드 페이지"""
    st.title("🏭 Factory Dashboard")
    
    # 요약 정보
    summary = factory_manager.get_factory_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 팩토리", summary['total_factories'])
    with col2:
        st.metric("정상", summary['normal_count'], delta=None, delta_color="normal")
    with col3:
        st.metric("경고", summary['warning_count'], delta=None, delta_color="normal")
    with col4:
        st.metric("위험", summary['error_count'], delta=None, delta_color="inverse")
    
    st.write("---")
    
    # 팩토리 관리 섹션
    with st.expander("🏗️ 새 팩토리 추가", expanded=False):
        col_name, col_location = st.columns(2)
        with col_name:
            factory_name = st.text_input("팩토리 이름")
        with col_location:
            factory_location = st.text_input("위치")
        
        if st.button("팩토리 추가"):
            if factory_name and factory_location:
                factory_id = factory_manager.add_factory(factory_name, factory_location)
                st.success(f"팩토리 '{factory_name}'가 추가되었습니다! (ID: {factory_id})")
                st.rerun()
            else:
                st.error("팩토리 이름과 위치를 모두 입력해주세요.")
    
    # 팩토리 목록
    st.subheader("🏭 팩토리 현황")
    
    if summary['total_factories'] == 0:
        st.write("등록된 팩토리가 없습니다. 새 팩토리를 추가해보세요!")
        return
    
    for factory_status in summary['factories']:
        display_factory_card(factory_status, factory_manager)
    
    st.write("---")
    
    # 팩토리 피드
    st.subheader("📱 팩토리 피드")
    factory_feed = factory_manager.get_factory_feed(10)
    
    if len(factory_feed) == 0:
        st.write("팩토리 활동이 없습니다.")
    else:
        for _, post in factory_feed.iterrows():
            display_factory_post(post)
    
    # 소셜 피드 통합 버튼
    st.write("---")
    if st.button("🔄 소셜 피드에 팩토리 상태 업데이트", type="primary"):
        integrate_factory_with_social_feed(post_manager, factory_manager)
        st.success("팩토리 상태가 소셜 피드에 업데이트되었습니다!")
        st.rerun()

def display_factory_card(factory_status, factory_manager):
    """팩토리 카드 표시"""
    status_colors = {
        'normal': '#28a745',
        'overheat': '#dc3545',
        'low_pressure': '#ffc107',
        'rpm_issue': '#ffc107'
    }
    
    status_emojis = {
        'normal': '✅',
        'overheat': '🔥',
        'low_pressure': '⚠️',
        'rpm_issue': '⚙️'
    }
    
    color = status_colors.get(factory_status['status'], '#6c757d')
    emoji = status_emojis.get(factory_status['status'], '❓')
    
    with st.container():
        st.markdown(f"""
        <div style="
            border-left: 5px solid {color};
            padding: 15px;
            margin: 10px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            color: #333333;
        ">
        <h4>{emoji} {factory_status['factory_name']}</h4>
        <p><strong>상태:</strong> {factory_status['status']}</p>
        <p><strong>온도:</strong> {factory_status['temperature']}°C | 
           <strong>압력:</strong> {factory_status['pressure']}bar | 
           <strong>RPM:</strong> {factory_status['rpm']}</p>
        <p><strong>생산량:</strong> {factory_status['product_count']}/시간</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"🔄 상태 업데이트", key=f"update_{factory_status['factory_name']}"):
                factory_manager.update_factory_status(factory_status.get('factory_id', factory_status['factory_name']))
                st.rerun()
        
        with col2:
            if st.button(f"⚠️ 강제 이상", key=f"force_{factory_status['factory_name']}"):
                factory_manager.update_factory_status(factory_status.get('factory_id', factory_status['factory_name']), force_abnormal=True)
                st.rerun()
        
        with col3:
            if st.button(f"📊 상세 분석", key=f"detail_{factory_status['factory_name']}"):
                st.session_state.current_page = 'factory_detail'
                st.session_state.selected_factory_id = factory_status.get('factory_id', factory_status['factory_name'])
                st.rerun()

def display_factory_post(post):
    """팩토리 포스트 표시"""
    priority_colors = {
        'high': '#dc3545',
        'normal': '#28a745'
    }
    
    color = priority_colors.get(post['priority'], '#6c757d')
    
    with st.container():
        st.markdown(f"""
        <div style="
            border-left: 5px solid {color};
            padding: 15px;
            margin: 10px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            color: #333333;
        ">
        <p><strong>{post['message']}</strong></p>
        <small>📅 {post['created_at']}</small>
        </div>
        """, unsafe_allow_html=True)

def factory_detail_page(factory_manager):
    """팩토리 상세 분석 페이지"""
    st.title("📊 팩토리 상세 분석")
    
    if st.button("← 대시보드로 돌아가기"):
        st.session_state.current_page = 'factory_dashboard'
        if 'selected_factory_id' in st.session_state:
            del st.session_state['selected_factory_id']
        st.rerun()
    
    factory_id = st.session_state.get('selected_factory_id')
    if not factory_id:
        st.error("팩토리를 찾을 수 없습니다.")
        return
    
    factory = factory_manager.get_factory_by_id(factory_id)
    if not factory:
        st.error("삭제된 팩토리입니다.")
        return
    
    st.write("---")
    
    # 팩토리 기본 정보
    status = factory.current_status()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(f"🏭 {factory.name}")
        st.write(f"**위치:** {getattr(factory, 'location', '미지정')}")
        st.write(f"**ID:** {factory_id}")
        st.write(f"**현재 상태:** {status['status']}")
    
    with col2:
        # 실시간 메트릭
        col_temp, col_pressure = st.columns(2)
        with col_temp:
            temp_delta = status['temperature'] - factory.base_temp
            st.metric("온도", f"{status['temperature']:.1f}°C", 
                     delta=f"{temp_delta:+.1f}°C",
                     delta_color="inverse" if temp_delta > 20 else "normal")
        
        with col_pressure:
            pressure_delta = status['pressure'] - factory.base_pressure
            st.metric("압력", f"{status['pressure']:.1f}bar", 
                     delta=f"{pressure_delta:+.1f}bar",
                     delta_color="inverse" if pressure_delta < -20 else "normal")
        
        col_rpm, col_prod = st.columns(2)
        with col_rpm:
            rpm_delta = status['rpm'] - factory.base_rpm
            st.metric("RPM", f"{status['rpm']:.1f}", 
                     delta=f"{rpm_delta:+.1f}",
                     delta_color="inverse" if rpm_delta < -10 else "normal")
        
        with col_prod:
            prod_delta = status['product_count'] - factory.base_product
            st.metric("생산량", f"{status['product_count']:.1f}/h", 
                     delta=f"{prod_delta:+.1f}/h")
    
    st.write("---")
    
    # 기준값 대비 분석
    st.subheader("📈 성능 분석")
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    
    # 온도 분석
    temp_data = [factory.base_temp, status['temperature']]
    temp_colors = ['blue', 'red' if status['temperature'] > factory.base_temp + 20 else 'green']
    ax1.bar(['기준값', '현재값'], temp_data, color=temp_colors)
    ax1.set_title('온도 비교 (°C)')
    ax1.set_ylabel('온도')
    
    # 압력 분석
    pressure_data = [factory.base_pressure, status['pressure']]
    pressure_colors = ['blue', 'orange' if status['pressure'] < factory.base_pressure - 20 else 'green']
    ax2.bar(['기준값', '현재값'], pressure_data, color=pressure_colors)
    ax2.set_title('압력 비교 (bar)')
    ax2.set_ylabel('압력')
    
    # RPM 분석
    rpm_data = [factory.base_rpm, status['rpm']]
    rpm_colors = ['blue', 'purple' if status['rpm'] < factory.base_rpm - 10 else 'green']
    ax3.bar(['기준값', '현재값'], rpm_data, color=rpm_colors)
    ax3.set_title('RPM 비교')
    ax3.set_ylabel('RPM')
    
    # 생산량 분석
    prod_data = [factory.base_product, status['product_count']]
    prod_colors = ['blue', 'darkgreen']
    ax4.bar(['기준값', '현재값'], prod_data, color=prod_colors)
    ax4.set_title('생산량 비교 (시간당)')
    ax4.set_ylabel('생산량')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # 권장 조치사항
    st.write("---")
    st.subheader("💡 권장 조치사항")
    
    recommendations = []
    
    if status['temperature'] > factory.base_temp + 30:
        recommendations.append("🔥 **긴급**: 냉각 시스템 점검 및 온도 조절 필요")
    elif status['temperature'] > factory.base_temp + 15:
        recommendations.append("⚠️ **주의**: 온도 상승 모니터링 강화")
    
    if status['pressure'] < factory.base_pressure - 30:
        recommendations.append("⚠️ **긴급**: 압력 공급 시스템 점검 필요")
    elif status['pressure'] < factory.base_pressure - 15:
        recommendations.append("💡 **권장**: 압력 레벨 조정 검토")
    
    if status['rpm'] < factory.base_rpm - 15:
        recommendations.append("⚙️ **긴급**: 구동 시스템 점검 및 정비 필요")
    elif status['rpm'] < factory.base_rpm - 5:
        recommendations.append("🔧 **권장**: 기계 윤활 및 정비 점검")
    
    if status['status'] == 'normal':
        recommendations.append("✅ **정상**: 현재 모든 시스템이 정상 범위에서 작동 중입니다")
    
    if recommendations:
        for rec in recommendations:
            st.write(rec)
    else:
        st.write("✅ 현재 특별한 조치사항이 없습니다.")