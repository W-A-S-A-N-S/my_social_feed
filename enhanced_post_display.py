# enhanced_post_display.py - 향상된 포스트 표시 (기존 post.py에 추가할 함수들)
import json
import matplotlib.pyplot as plt
import streamlit as st
import os

def display_enhanced_post(post, post_manager, current_username, show_actions=True, auth_manager=None):
    """개별 게시물 표시 (팩토리 포스트 지원 강화)"""
    with st.container():
        # 게시물 정보
        col1, col2, col3 = st.columns([1, 5, 1])
        
        with col1:
            # 시스템 사용자(팩토리)인지 확인
            if post['username'] == "🏭_Factory_System":
                st.markdown("<div style='font-size: 50px; text-align: center;'>🏭</div>", 
                           unsafe_allow_html=True)
            else:
                display_profile_emoji(auth_manager, post['username'], size=50)
        
        with col2:
            # 팩토리 시스템 포스트 특별 표시
            if post['username'] == "🏭_Factory_System":
                st.markdown(f"**🏭 Factory System** · {post['created_at']}")
            else:
                st.markdown(f"**{post['username']}** · {post['created_at']}")
            
            # 게시물 내용 표시
            is_data_post = False
            is_factory_post = False
            is_emergency_post = False
            
            if isinstance(post['content'], str):
                try:
                    content_data = json.loads(post['content'])
                    if content_data and isinstance(content_data, dict):
                        
                        # 일반 데이터 차트
                        if content_data.get('type') == 'chart':
                            is_data_post = True
                            display_data_chart(content_data)
                        
                        # 팩토리 상태 포스트
                        elif content_data.get('type') == 'factory_status':
                            is_factory_post = True
                            display_factory_status_chart(content_data)
                        
                        # 팩토리 긴급 상황 포스트
                        elif content_data.get('type') == 'factory_emergency':
                            is_emergency_post = True
                            display_emergency_alert(content_data)
                            
                except (json.JSONDecodeError, AttributeError):
                    pass
            
            # 일반 텍스트 포스트 및 리포스트 처리
            if not is_data_post and not is_factory_post and not is_emergency_post:
                display_regular_post_content(post, post_manager)

        with col3:
            if st.button("📄", key=f"detail_{post['post_id']}", help="게시물 상세보기"):
                st.session_state.current_page = 'post_detail'
                st.session_state.selected_post_id = post['post_id']
                st.rerun()
        
        # 액션 버튼 (팩토리 시스템 포스트는 제외)
        if show_actions and post['username'] != "🏭_Factory_System":
            display_post_actions(post, post_manager, current_username)
        elif post['username'] == "🏭_Factory_System":
            display_factory_post_info(post)
        
        st.write("---")

def display_data_chart(content_data):
    """일반 데이터 차트 표시"""
    st.markdown(f"### {content_data.get('title', '데이터 비교')}")
    
    data = content_data.get('data', {})
    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title(content_data.get('title'))
    st.pyplot(fig)

def display_factory_status_chart(content_data):
    """팩토리 상태 차트 표시"""
    st.markdown(f"### 🏭 {content_data.get('title', '팩토리 상태')}")
    
    # 상태 정보 표시
    status = content_data.get('status', 'unknown')
    priority = content_data.get('priority', 'normal')
    
    status_colors = {
        'normal': '🟢',
        'overheat': '🔴',
        'low_pressure': '🟡',
        'rpm_issue': '🟡'
    }
    
    status_emoji = status_colors.get(status, '⚪')
    
    # 우선순위에 따른 배경색
    if priority == 'high':
        st.markdown(
            f"""<div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
            <strong>상태:</strong> {status_emoji} {status.upper()}
            </div>""", 
            unsafe_allow_html=True
        )
    else:
        st.markdown(f"**상태:** {status_emoji} {status}")
    
    # 실시간 데이터 차트
    data = content_data.get('data', {})
    if data:
        display_factory_metrics_chart(data, status)
        display_factory_metrics_table(data)

def display_emergency_alert(content_data):
    """긴급 상황 알림 표시"""
    st.markdown(f"### 🚨 {content_data.get('title', '긴급 상황')}")
    
    # 긴급 상황 배경
    st.markdown(
        """<div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 5px solid #dc3545;">
        <h4 style="color: #721c24; margin: 0;">⚠️ EMERGENCY ALERT ⚠️</h4>
        </div>""", 
        unsafe_allow_html=True
    )
    
    alert_type = content_data.get('alert_type', 'unknown')
    data = content_data.get('data', {})
    
    # 긴급도별 메시지
    if alert_type == 'overheat':
        st.error(f"🔥 과열 상황! 온도: {data.get('온도', 'N/A')}°C")
    elif alert_type == 'low_pressure':
        st.warning(f"💨 압력 부족! 압력: {data.get('압력', 'N/A')}bar")
    elif alert_type == 'rpm_issue':
        st.warning(f"⚙️ RPM 이상! RPM: {data.get('RPM', 'N/A')}")
    
    # 긴급 상황 데이터 표시
    if data:
        display_emergency_data_chart(data, alert_type)

def display_factory_metrics_chart(data, status):
    """팩토리 메트릭 차트 표시"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))
    
    # 온도 차트 (위험 수준에 따른 색상)
    temp = data.get('온도', 0)
    temp_color = 'red' if temp > 220 else 'orange' if temp > 200 else 'green'
    ax1.bar(['온도'], [temp], color=temp_color)
    ax1.set_title('온도 (°C)')
    ax1.set_ylim(0, 300)
    ax1.axhline(y=220, color='red', linestyle='--', alpha=0.7, label='위험선')
    ax1.legend()
    
    # 압력 차트
    pressure = data.get('압력', 0)
    pressure_color = 'orange' if pressure < 120 else 'green'
    ax2.bar(['압력'], [pressure], color=pressure_color)
    ax2.set_title('압력 (bar)')
    ax2.set_ylim(0, 200)
    ax2.axhline(y=120, color='orange', linestyle='--', alpha=0.7, label='주의선')
    ax2.legend()
    
    # RPM 차트
    rpm = data.get('RPM', 0)
    rpm_color = 'purple' if rpm < 35 else 'cyan'
    ax3.bar(['RPM'], [rpm], color=rpm_color)
    ax3.set_title('속도 (RPM)')
    ax3.set_ylim(0, 100)
    ax3.axhline(y=35, color='purple', linestyle='--', alpha=0.7, label='주의선')
    ax3.legend()
    
    # 생산량 차트
    production = data.get('생산량', 0)
    ax4.bar(['생산량'], [production], color='darkgreen')
    ax4.set_title('생산량 (시간당)')
    ax4.set_ylim(0, 150)
    
    plt.tight_layout()
    st.pyplot(fig)

def display_factory_metrics_table(data):
    """팩토리 메트릭 테이블 표시"""
    col_temp, col_pressure, col_rpm, col_prod = st.columns(4)
    
    with col_temp:
        temp = data.get('온도', 0)
        temp_delta_color = "inverse" if temp > 220 else "normal"
        st.metric("온도", f"{temp:.1f}°C", delta_color=temp_delta_color)
        
    with col_pressure:
        pressure = data.get('압력', 0)
        pressure_delta_color = "inverse" if pressure < 120 else "normal"
        st.metric("압력", f"{pressure:.1f}bar", delta_color=pressure_delta_color)
        
    with col_rpm:
        rpm = data.get('RPM', 0)
        rpm_delta_color = "inverse" if rpm < 35 else "normal"
        st.metric("RPM", f"{rpm:.1f}", delta_color=rpm_delta_color)
        
    with col_prod:
        production = data.get('생산량', 0)
        st.metric("생산량", f"{production:.1f}/h")

def display_emergency_data_chart(data, alert_type):
    """긴급 상황 데이터 차트"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    metrics = ['온도', '압력', 'RPM', '생산량']
    values = [data.get(metric, 0) for metric in metrics]
    
    # 위험 수준에 따른 색상
    colors = []
    for i, (metric, value) in enumerate(zip(metrics, values)):
        if alert_type == 'overheat' and metric == '온도':
            colors.append('red')
        elif alert_type == 'low_pressure' and metric == '압력':
            colors.append('orange')
        elif alert_type == 'rpm_issue' and metric == 'RPM':
            colors.append('purple')
        else:
            colors.append('gray')
    
    bars = ax.bar(metrics, values, color=colors)
    ax.set_title('🚨 긴급 상황 데이터')
    
    # 값 표시
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    st.pyplot(fig)

def display_regular_post_content(post, post_manager):
    """일반 포스트 내용 표시"""
    if post.get('is_repost') and post.get('original_post_id'):
        if post.get('content'):
            st.write(post['content'])
            st.markdown("---")
        
        original_post = post_manager.get_post_by_id(post['original_post_id'])
        if original_post:
            st.markdown("🔄 **리포스트된 게시물:**")
            st.markdown(f"**{original_post['username']}** · {original_post['created_at']}")
            st.write(original_post['content'])
            
            if original_post.get('has_image') and original_post.get('image_path'):
                original_image_path = original_post.get('image_path')
                if original_image_path and isinstance(original_image_path, str) and os.path.exists(original_image_path):
                    st.image(original_image_path, width=400)
                else:
                    st.write("*이미지를 불러올 수 없습니다.*")
        else:
            st.write("*삭제된 게시물입니다.*")
    else:
        if post.get('content') is not None:
            st.write(post['content'])

    if post.get('has_image') and post.get('image_path'):
        image_path = post.get('image_path')
        if image_path and isinstance(image_path, str) and os.path.exists(image_path):
            st.image(image_path, width=400)
        else:
            st.write("*이미지를 불러올 수 없습니다.*")

def display_post_actions(post, post_manager, current_username):
    """일반 포스트 액션 버튼"""
    col_like, col_repost, col_stats = st.columns([1, 1, 4])
    
    with col_like:
        liked = post_manager.user_liked_post(post['post_id'], current_username)
        like_emoji = "❤️" if liked else "🤍"
        if st.button(f"{like_emoji} {post['like_count']}", key=f"like_{post['post_id']}"):
            post_manager.toggle_like(post['post_id'], current_username)
            st.rerun()
    
    with col_repost:
        if st.button(f"🔄 {post['repost_count']}", key=f"repost_{post['post_id']}"):
            st.session_state[f"show_repost_{post['post_id']}"] = True
            st.rerun()
    
    if st.session_state.get(f"show_repost_{post['post_id']}", False):
        with st.expander("리포스트하기", expanded=True):
            repost_comment = st.text_area("코멘트 추가 (선택사항)", key=f"repost_comment_{post['post_id']}")
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.button("리포스트하기", key=f"submit_repost_{post['post_id']}"):
                    success, message = post_manager.create_repost(current_username, post['post_id'], repost_comment)
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

def display_factory_post_info(post):
    """팩토리 포스트 정보 표시"""
    st.markdown("🏭 **Factory Alert**")
    
    # 팩토리 포스트 특별 정보 표시
    try:
        if isinstance(post.get('content'), str):
            content_data = json.loads(post['content'])
            if content_data.get('priority') == 'emergency':
                st.markdown("🚨 **긴급 알림**")
            elif content_data.get('priority') == 'high':
                st.markdown("⚠️ **높은 우선순위**")
    except:
        pass

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