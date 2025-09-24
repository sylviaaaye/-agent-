from langchain.prompts import PromptTemplate, ChatPromptTemplate

JD_ANALYSIS_TEMPLATE_WITH_RAG = [
    ("system", 
     "作为一位资深的技术面试官和职业顾问，请基于以下信息为求职者提供详细的分析和建议。"
     "如果提供了【个人知识库参考】，请在生成建议时优先结合这些内容，这将使你的分析更具个性化和深度。"
    ),
    ("human", 
    "### 【个人知识库参考】\n"
    "<context>\n{context}\n</context>\n\n"
    "### 【职位描述(JD)】\n"
    "{jd_content}\n\n"
    "### 【求职者简历】\n"
    "{resume_content}\n\n"
    "请严格按照以下格式提供分析（使用Markdown格式）：\n\n"
    "## 1. 岗位匹配度分析\n"
    "- 技能匹配度评分（0-100）\n"
    "- 列出匹配的关键技能\n"
    "- 指出需要补充的技能差距\n\n"
    "## 2. 推荐重点准备的项目经验\n"
    "- 从简历中选择最相关的2-3个项目\n"
    "- 建议重点准备的项目难点和亮点\n"
    "- 如何将项目经验与岗位需求对应\n\n"
    "## 3. 面试重点准备方向\n"
    "### 3.1 技术面试考点\n"
    "- 必考的算法题类型\n"
    "- 系统设计相关问题\n"
    "- 技术细节考察重点\n\n"
    "### 3.2 软实力面试\n"
    "- 项目管理能力\n"
    "- 团队协作经历\n"
    "- 技术选型决策\n\n"
    "## 4. 学习资源推荐\n"
    "### 4.1 技术栈资料\n"
    "- 官方文档链接\n"
    "- 推荐的学习路径\n"
    "- 进阶技术博客\n\n"
    "### 4.2 面试题库\n"
    "- LeetCode相关题目推荐\n"
    "- 系统设计参考资料\n"
    "- 行业最佳实践\n\n"
    "## 5. 差异化竞争建议\n"
    "- 如何突出个人优势\n"
    "- 准备独特的技术亮点\n"
    "- 如何应对竞争者\n\n"
    "请确保建议具体且可操作，帮助求职者针对性地准备面试。"
    )
]

jd_analysis_prompt = ChatPromptTemplate.from_messages(JD_ANALYSIS_TEMPLATE_WITH_RAG)


# --- 原有的模板，保留作为备份或用于无RAG的场景 ---
JD_ANALYSIS_TEMPLATE_LEGACY = """
作为一位资深的技术面试官和职业顾问，请基于以下信息为求职者提供详细的分析和建议：

职位描述(JD)：
{jd_content}

求职者简历：
{resume_content}

请按照以下格式提供分析（使用Markdown格式）：

## 1. 岗位匹配度分析
- 技能匹配度评分（0-100）
- 列出匹配的关键技能
- 指出需要补充的技能差距

## 2. 推荐重点准备的项目经验
- 从简历中选择最相关的2-3个项目
- 建议重点准备的项目难点和亮点
- 如何将项目经验与岗位需求对应

## 3. 面试重点准备方向
### 3.1 技术面试考点
- 必考的算法题类型
- 系统设计相关问题
- 技术细节考察重点

### 3.2 软实力面试
- 项目管理能力
- 团队协作经历
- 技术选型决策

## 4. 学习资源推荐
### 4.1 技术栈资料
- 官方文档链接
- 推荐的学习路径
- 进阶技术博客

### 4.2 面试题库
- LeetCode相关题目推荐
- 系统设计参考资料
- 行业最佳实践

## 5. 差异化竞争建议
- 如何突出个人优势
- 准备独特的技术亮点
- 如何应对竞争者

请确保建议具体且可操作，帮助求职者针对性地准备面试。
"""

jd_analysis_prompt_legacy = PromptTemplate(
    input_variables=["jd_content", "resume_content"],
    template=JD_ANALYSIS_TEMPLATE_LEGACY
)


# --- 新增：用于生成面试任务计划的模板 ---

TASK_GENERATION_TEMPLATE = """
作为一位专业的面试教练和时间管理大师，请根据以下这份【求职者与岗位的匹配度分析报告】和【面试日期信息】，为用户生成一个高度个性化、可执行的面试准备任务清单。

---
### **【求职者与岗位的匹配度分析报告】**
{jd_analysis_result}
---

### **【面试日期信息】**
- 距离面试还有: {days_to_interview} 天
- 今天的日期是: {today_date}
- 面试的日期是: {interview_date}

---

### **【你的任务】**
请你为用户创建一个从今天开始，直到面试前一天的每日学习和准备计划。
你的计划必须严格遵循以下原则：

1.  **高度相关**: 计划的【核心目标】是解决“匹配度分析报告”中提到的【技能差距】和【需要补充的知识点】。所有任务都应围绕此展开。
2.  **突出重点**: 优先安排时间复习报告中提到的【匹配的关键技能】和【推荐重点准备的项目经验】，确保长处更长。
3.  **结构清晰**: 使用Markdown格式，以日期和星期为单位进行组织。
4.  **任务具体**: 每天的任务要明确、可量化（例如：“针对【技能差距：C++并发编程】，学习并实现一个生产者-消费者模型”、“复盘【项目经验：智能求职Agent】中的LangChain调用链路”）。
5.  **循序渐进**: 早期侧重于基础和技能差距，中期进行综合练习和项目复盘，后期专注模拟面试和心态调整。
6.  **激励人心**: 在每天的计划开始或结束时，加入一句简短的激励语。
7.  **劳逸结合**: 合理安排休息。

请以“### 🚨 面试倒计时：{days_to_interview} 天 🚨”为标题开始你的计划。
"""

task_generation_prompt = PromptTemplate(
    input_variables=["jd_analysis_result", "days_to_interview", "today_date", "interview_date"],
    template=TASK_GENERATION_TEMPLATE
) 

# --- Agent System Prompt ---

# 这是我们为 Agent 大脑设定的"操作系统"和"行为准则"
# 它告诉 Agent 它的身份、它拥有的工具、以及它应该如何思考和行动。
# `{tools}` 和 `{tool_names}` 是 LangChain Agent Executor 会自动填充的占位符。
# `{input}` 是用户的原始请求。
# `{agent_scratchpad}` 是 Agent 的"记忆"，用来存放它之前的每一步思考、行动和观察结果。

AGENT_PROMPT_TEMPLATE = """你是一个专业的求职助手Agent。请使用提供的工具来帮助用户完成求职分析任务。

可用工具：
{tools}

使用以下格式回答问题：

Question: 用户的输入问题
Thought: 我需要分析这个问题并决定使用哪个工具
Action: 工具名称
Action Input: {{"参数名1": "参数值1", "参数名2": "参数值2"}}
Observation: 工具执行的结果
... (思考/行动/观察可以重复多次)
Thought: 我现在知道最终答案了
Final Answer: 对用户输入问题的最终答案

工具使用示例：
- 分析JD时: Action: jd_analysis, Action Input: {{"jd_content": "职位内容", "resume_content": "简历内容"}}
- 生成计划时: Action: interview_schedule, Action Input: {{"jd_analysis_result": "分析结果", "interview_date": "2024-08-30"}}
- 查询知识库: Action: knowledge_base_query, Action Input: {{"query": "查询内容"}}
- 跟踪进度: Action: progress_tracking, Action Input: {{"current_progress": "当前进度"}}

重要提示：
1. Action Input必须是有效的JSON格式
2. 参数名必须与工具定义完全匹配
3. 请确保所有必需参数都已提供
4. 如果遇到API限流，请在Final Answer中说明并建议使用离线模式

Question: {input}
{agent_scratchpad}"""

# 使用 LangChain 的 PromptTemplate 类来实例化这个模板
# 这样 LangChain 就能正确地识别和处理其中的占位符
agent_system_prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
    template=AGENT_PROMPT_TEMPLATE
) 