import streamlit as st
from dotenv import load_dotenv
from prompts import jd_analysis_prompt
from utils import analyze_job_description, validate_inputs

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="求职助手 - JD分析",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        margin-top: 20px;
    }
    .success {
        padding: 20px;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
        margin: 10px 0;
    }
    .error {
        padding: 20px;
        border-radius: 5px;
        background-color: #f8d7da;
        color: #721c24;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏配置
with st.sidebar:
    st.title("⚙️ 分析设置")
    temperature = st.slider(
        "分析灵活度",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        help="较低的值会产生更确定性的回答，较高的值会产生更有创意的回答"
    )
    
    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.markdown("""
    1. 粘贴完整的职位描述(JD)
    2. 粘贴简历主要内容
    3. 调整分析灵活度
    4. 点击分析按钮获取建议
    """)
    
    st.markdown("---")
    st.markdown("### ℹ️ 关于")
    st.markdown("""
    本工具使用AI技术分析职位要求与个人简历的匹配度，
    并提供针对性的面试准备建议。
    """)

# 主界面
st.title("🎯 求职助手 - JD分析")
st.write("智能分析职位描述，提供个性化面试准备建议")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 职位描述 (JD)")
    jd_content = st.text_area(
        "请粘贴完整的职位描述",
        height=300,
        placeholder="在此粘贴职位描述...",
        help="建议包含：职位要求、工作职责、技能要求等"
    )

with col2:
    st.subheader("📝 个人简历")
    resume_content = st.text_area(
        "请粘贴简历内容",
        height=300,
        placeholder="在此粘贴简历主要内容...",
        help="建议包含：技术栈、项目经验、教育背景等"
    )

# 分析按钮
if st.button("🚀 开始分析", type="primary"):
    # 验证输入
    is_valid, error_msg = validate_inputs(jd_content, resume_content)
    
    if not is_valid:
        st.error(error_msg)
    else:
        with st.spinner("🤔 正在深入分析中，请稍候..."):
            # 调用分析函数
            result, error = analyze_job_description(
                jd_analysis_prompt,
                jd_content,
                resume_content,
                temperature
            )
            
            if error:
                st.error(error)
            else:
                st.success("✅ 分析完成！")
                st.markdown(result)
                
                # 添加下载按钮
                st.download_button(
                    label="📥 下载分析报告",
                    data=result,
                    file_name="jd_analysis_report.md",
                    mime="text/markdown"
                ) 