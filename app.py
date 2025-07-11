import streamlit as st
from dotenv import load_dotenv
import os
import datetime
from prompts import jd_analysis_prompt, task_generation_prompt
from utils import analyze_job_description, validate_inputs, generate_interview_schedule

# --- .env 文件加载与调试 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
found_dotenv = load_dotenv(dotenv_path=dotenv_path, override=True)

# --- 页面配置 (必须是第一个st命令) ---
st.set_page_config(
    page_title="求职助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 初始化 Session State ---
if 'jd_analysis_result' not in st.session_state:
    st.session_state.jd_analysis_result = None

# --- 侧边栏 ---
with st.sidebar:
    st.title("🛠️ 全局设置")
    
    # 调试信息
    st.divider()
    st.subheader("调试信息")
    if found_dotenv:
        st.success(f"成功加载 .env 文件")
    else:
        st.error(f"未找到 .env 文件")
    
    api_key_loaded = os.getenv("MOONSHOT_API_KEY")
    if api_key_loaded:
        st.success("✅ API Key 已加载")
    else:
        st.error("❌ API Key 未加载")
        st.stop()
    
    # 通用设置
    st.divider()
    st.subheader("分析设置")
    temperature = st.slider(
        "AI分析灵活度", 0.0, 1.0, 0.7,
        help="值越低，输出越稳定；值越高，越有创意。"
    )

# --- 主界面：标签页布局 ---
tab1, tab2 = st.tabs(["🎯 **第一步：JD 分析**", "📅 **第二步：生成冲刺计划**"])

# --- 标签页1: JD 分析 ---
with tab1:
    st.header("智能分析职位描述，提供个性化面试准备建议")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 职位描述 (JD)")
        jd_content = st.text_area("粘贴JD", height=300, key="jd_input", help="建议包含：职位要求、工作职责、技能要求等")
    with col2:
        st.subheader("📝 个人简历")
        resume_content = st.text_area("粘贴简历", height=300, key="resume_input", help="建议包含：技术栈、项目经验、教育背景等")

    if st.button("🚀 开始分析", key="analyze_jd", type="primary"):
        is_valid, error_msg = validate_inputs(jd_content, resume_content)
        if not is_valid:
            st.error(error_msg)
        else:
            with st.spinner("🤔 正在深入分析中，请稍候..."):
                result, error = analyze_job_description(jd_analysis_prompt, jd_content, resume_content, temperature)
                if error:
                    st.error(error)
                else:
                    st.success("✅ 分析完成！现在可以去“生成冲刺计划”标签页，为你量身定制学习计划了。")
                    # 将结果存入 session_state
                    st.session_state.jd_analysis_result = result
                    st.markdown(result)
                    st.download_button("📥 下载分析报告", result, "jd_analysis_report.md", "text/markdown")

# --- 标签页2: 面试任务规划 ---
with tab2:
    st.header("根据JD分析报告，为你量身定制冲刺计划")

    # 检查是否已完成JD分析
    if st.session_state.jd_analysis_result:
        st.info("检测到已生成的JD分析报告，将基于此报告为您生成冲刺计划。")
        
        with st.expander("点击查看JD分析报告"):
            st.markdown(st.session_state.jd_analysis_result)

        interview_date = st.date_input(
            "请选择你的面试日期",
            value=datetime.date.today() + datetime.timedelta(days=14),
            min_value=datetime.date.today(),
            help="选择你的最终面试日期，系统将为你生成从今天到面试前一天的每日计划。"
        )

        if st.button("🚀 生成个性化冲刺计划", key="generate_schedule", type="primary"):
            with st.spinner("📅 正在为你规划学习路径，请稍候..."):
                # 传入JD分析结果
                result, error = generate_interview_schedule(
                    task_generation_prompt, 
                    interview_date, 
                    st.session_state.jd_analysis_result,  # 从session_state获取
                    temperature
                )
                if error:
                    st.error(error)
                else:
                    st.success("✅ 个性化冲刺计划生成完毕！")
                    st.markdown(result)
                    st.download_button(
                        "📥 下载冲刺计划", result, 
                        f"interview_schedule_to_{interview_date.strftime('%Y-%m-%d')}.md",
                        "text/markdown", key="download_schedule"
                    )
    else:
        st.warning("⚠️ 请先在“第一步：JD 分析”标签页中完成一次成功的分析，才能生成个性化的冲刺计划。")
        st.image("https://img.icons8.com/plasticine/100/000000/arrow.png", width=100)
