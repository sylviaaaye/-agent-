import streamlit as st
from dotenv import load_dotenv
import os
import datetime
from prompts import jd_analysis_prompt, task_generation_prompt
from utils import analyze_job_description, validate_inputs, generate_interview_schedule
from agent_executor import create_job_search_agent, JobSearchAgent

# --- .env 文件加载与调试 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
found_dotenv = load_dotenv(dotenv_path=dotenv_path, override=True)

# --- 页面配置 (必须是第一个st命令) ---
st.set_page_config(
    page_title="智能求职助手 Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 初始化 Session State ---
if 'jd_analysis_result' not in st.session_state:
    st.session_state.jd_analysis_result = None
if 'agent_mode' not in st.session_state:
    st.session_state.agent_mode = False
if 'agent_instance' not in st.session_state:
    st.session_state.agent_instance = None

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
    
    # 模式选择
    st.divider()
    st.subheader("运行模式")
    agent_mode = st.checkbox(
        "🤖 启用 Agent 模式",
        value=st.session_state.agent_mode,
        help="Agent模式将自动完成所有任务，包括JD分析、计划生成和知识库查询"
    )
    st.session_state.agent_mode = agent_mode
    
    if agent_mode:
        st.info("Agent模式已启用！系统将自动完成所有任务。")
    else:
        st.info("传统模式：手动分步骤执行。")
    
    # 通用设置
    st.divider()
    st.subheader("分析设置")
    temperature = st.slider(
        "AI分析灵活度", 0.0, 1.0, 0.7,
        help="值越低，输出越稳定；值越高，越有创意。"
    )

# --- 主界面：标签页布局 ---
if agent_mode:
    # Agent模式：单标签页，一站式服务
    st.title("🤖 智能求职助手 Agent")
    st.markdown("**Agent模式**：输入信息后，AI将自动完成所有分析、规划和推荐任务！")
    
    # Agent状态显示
    if st.session_state.agent_instance is None:
        try:
            st.session_state.agent_instance = create_job_search_agent(temperature)
            st.success("✅ Agent 初始化成功！")
        except Exception as e:
            st.error(f"❌ Agent 初始化失败：{str(e)}")
            st.stop()
    
    # 离线测试选项
    offline_mode = st.checkbox(
        "🔧 离线测试模式（不调用API）",
        help="启用此模式将使用模拟数据，避免API限流问题"
    )
    
    if offline_mode:
        st.info("🔧 离线测试模式已启用，将使用模拟数据")
        
        # 模拟Agent执行
        if st.button("🚀 模拟Agent工作", key="mock_agent_work", type="primary"):
            with st.spinner("🤖 模拟Agent正在工作中..."):
                # 模拟结果
                mock_result = f"""
## 📊 模拟Agent分析结果

### 1. 岗位匹配度分析
- **技能匹配度评分：85/100**
- **匹配的关键技能：**
  - 机器学习基础（统计机器学习、在线机器学习课程）
  - 技术背景（电子与计算机工程硕士）
  - 团队协作能力（Unity实习经验）

- **需要补充的技能差距：**
  - 大模型实践经验
  - 数据标注和评测集构建
  - 产品策略制定经验

### 2. 推荐重点准备的项目经验
- **Unity实习项目：** 重点准备UI设计改进和需求文档撰写经验
- **机器学习课程项目：** 准备统计机器学习和在线机器学习的实际应用案例

### 3. 面试重点准备方向
#### 3.1 技术面试考点
- 机器学习算法原理
- 大模型基础知识
- 数据分析方法

#### 3.2 软实力面试
- 团队协作经历
- 需求分析和文档撰写
- 学习能力和适应能力

### 4. 学习资源推荐
#### 4.1 技术栈资料
- 《深度学习》（Goodfellow et al.）
- 《统计学习方法》（李航）
- 斯坦福CS231n课程

#### 4.2 面试题库
- LeetCode机器学习相关题目
- 产品经理面试常见问题
- 大模型应用案例分析

### 5. 差异化竞争建议
- 突出机器学习背景优势
- 准备具体的技术项目案例
- 展示快速学习能力

---
**模拟执行步骤：**
1. ✅ 分析职位描述和简历匹配度
2. ✅ 生成个性化学习计划
3. ✅ 查询知识库推荐资料
4. ✅ 整合最终报告

**执行了 3 个步骤**
"""
                
                st.success("✅ 模拟Agent任务完成！")
                st.markdown(mock_result)
                
                # 下载按钮
                st.download_button(
                    "📥 下载模拟报告", 
                    mock_result, 
                    f"mock_agent_report_{datetime.date.today().strftime('%Y-%m-%d')}.md",
                    "text/markdown"
                )
        
        st.stop()  # 停止后续执行
    
    # 输入区域
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 职位描述 (JD)")
        jd_content = st.text_area("粘贴JD", height=200, key="jd_input_agent", help="建议包含：职位要求、工作职责、技能要求等")
    with col2:
        st.subheader("📝 个人简历")
        resume_content = st.text_area("粘贴简历", height=200, key="resume_input_agent", help="建议包含：技术栈、项目经验、教育背景等")
    
    # 面试日期
    interview_date = st.date_input(
        "请选择你的面试日期",
        value=datetime.date.today() + datetime.timedelta(days=14),
        min_value=datetime.date.today(),
        help="选择你的最终面试日期"
    )
    
    # Agent执行按钮
    if st.button("🚀 Agent 开始工作", key="agent_work", type="primary"):
        if not jd_content.strip() or not resume_content.strip():
            st.error("请填写完整的职位描述和简历内容")
        else:
            with st.spinner("🤖 Agent 正在智能分析中，请稍候..."):
                try:
                    # 执行Agent
                    result = st.session_state.agent_instance.analyze_jd_and_generate_plan(
                        jd_content, 
                        resume_content, 
                        interview_date.strftime("%Y-%m-%d")
                    )
                    
                    if result["success"]:
                        st.success("✅ Agent 任务完成！")
                        
                        # 显示结果
                        st.markdown("## 📊 Agent 执行结果")
                        st.markdown(result["result"])
                        
                        # 显示执行步骤
                        with st.expander("🔍 查看 Agent 执行步骤"):
                            st.write(f"执行了 {result['iterations']} 个步骤")
                            for i, step in enumerate(result['steps'], 1):
                                st.write(f"**步骤 {i}:** {step}")
                        
                        # 下载按钮
                        st.download_button(
                            "📥 下载完整报告", 
                            result["result"], 
                            f"agent_report_{datetime.date.today().strftime('%Y-%m-%d')}.md",
                            "text/markdown"
                        )
                    else:
                        st.error(f"❌ Agent 执行失败：{result['error']}")
                        
                        # 如果是限流错误，提供详细解决方案
                        if "API限流" in result['error']:
                            st.warning("🚨 API限流解决方案：")
                            st.markdown("""
                            **方案1：使用离线测试模式**
                            - 勾选"🔧 离线测试模式（不调用API）"
                            - 点击"🚀 模拟Agent工作"
                            
                            **方案2：等待重试**
                            - 等待10-15分钟让API限流重置
                            - 重新点击"🚀 Agent 开始工作"
                            
                            **方案3：使用传统模式**
                            - 取消勾选"🤖 启用 Agent 模式"
                            - 使用分步骤的传统模式
                            """)
                        
                        if "suggestion" in result:
                            st.info(f"💡 建议：{result['suggestion']}")
                        
                except Exception as e:
                    st.error(f"❌ Agent 执行异常：{str(e)}")

else:
    # 传统模式：双标签页
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
                with st.spinner("🤔 正在深入分析中（知识库已启用），请稍候..."):
                    result, error = analyze_job_description(jd_content, resume_content, temperature)
                    if error:
                        st.error(error)
                    else:
                        st.success("✅ 分析完成！现在可以去\"生成冲刺计划\"标签页，为你量身定制学习计划了。")
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
            st.warning("⚠️ 请先在\"第一步: JD 分析\"标签页中完成一次成功的分析，才能生成个性化的冲刺计划。")
            st.image("https://img.icons8.com/plasticine/100/000000/arrow.png", width=100)

# --- 页脚信息 ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 智能求职助手 Agent | 基于 Moonshot + LangChain + RAG 技术构建</p>
    <p>💡 提示：启用 Agent 模式可获得更智能的一站式服务体验</p>
</div>
""", unsafe_allow_html=True) 