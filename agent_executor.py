import time
import json
from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from prompts import agent_system_prompt
from agent_tools import JDAnalysisTool, InterviewScheduleTool, KnowledgeBaseQueryTool, ProgressTrackingTool
import os

class JobSearchAgent:
    def __init__(self, llm: ChatOpenAI, tools: List[BaseTool]):
        self.llm = llm
        self.tools = tools
        
        # 获取工具名称列表
        tool_names = [tool.name for tool in tools]
        
        # 创建带有tool_names的prompt
        agent_prompt = agent_system_prompt.partial(tool_names=tool_names)
        
        self.agent = create_react_agent(llm, tools, agent_prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=tools, 
            verbose=True, 
            max_iterations=10,  # 增加最大迭代次数
            handle_parsing_errors=True,  # 处理解析错误
            return_intermediate_steps=True  # 返回中间步骤
        )
    
    def analyze_jd_and_generate_plan(self, jd_content: str, resume_content: str, interview_date: str) -> Dict[str, Any]:
        """
        分析JD并生成计划，包含智能限流处理
        """
        # 构建更明确的输入，减少内容长度
        user_input = f"""
请使用 jd_analysis 工具分析以下内容：

职位描述：{jd_content[:300]}
简历内容：{resume_content[:300]}

请提供详细的分析结果。
"""
        
        max_retries = 2  # 减少重试次数
        retry_delay = 15  # 增加初始延迟
        
        for attempt in range(max_retries):
            try:
                print(f"Agent执行尝试 {attempt + 1}/{max_retries}")
                
                # 在每次尝试前添加延迟
                if attempt > 0:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                
                # 执行Agent
                result = self.agent_executor.invoke({"input": user_input})
                
                # 检查结果是否完整
                output = result.get("output", "")
                if "Agent stopped due to iteration limit" in output or len(output.strip()) < 50:
                    # 如果结果不完整，返回基本信息
                    output = f"""
## 📊 Agent 分析结果

### 职位描述分析
- 职位描述长度：{len(jd_content)} 字符
- 简历内容长度：{len(resume_content)} 字符
- 面试日期：{interview_date}

### 建议
由于API限流，建议：
1. 使用离线测试模式查看完整分析
2. 或等待10分钟后重试
3. 或切换到传统模式进行分步骤分析

### 当前分析结果
{output}
"""
                
                # 如果成功，返回结果
                return {
                    "success": True,
                    "result": output,
                    "iterations": len(result.get("intermediate_steps", [])),
                    "steps": [f"步骤{i+1}: {step}" for i, step in enumerate(result.get("intermediate_steps", []))]
                }
                
            except Exception as e:
                error_str = str(e)
                print(f"尝试 {attempt + 1} 失败: {error_str}")
                
                # 检查是否是限流错误
                if "429" in error_str or "rate_limit" in error_str:
                    if attempt < max_retries - 1:
                        print(f"检测到API限流，将在 {retry_delay} 秒后重试...")
                        continue
                    else:
                        return {
                            "success": False,
                            "error": f"API限流，已重试{max_retries}次。请使用离线测试模式或等待10分钟后重试。",
                            "suggestion": "推荐使用离线测试模式，可立即查看完整分析结果"
                        }
                else:
                    # 其他错误，直接返回
                    return {
                        "success": False,
                        "error": f"Agent执行错误: {error_str}",
                        "suggestion": "请检查输入内容或使用传统模式"
                    }
        
        return {
            "success": False,
            "error": "API调用失败",
            "suggestion": "请使用离线测试模式或传统模式"
        }

def create_job_search_agent(temperature: float = 0.7) -> JobSearchAgent:
    """
    创建求职搜索Agent，包含智能限流处理
    """
    # 初始化LLM，增加重试和超时设置
    llm = ChatOpenAI(
        temperature=temperature,
        model_name="moonshot-v1-8k",
        openai_api_key=os.getenv("MOONSHOT_API_KEY"),
        openai_api_base="https://api.moonshot.cn/v1",
        max_tokens=4096,
        request_timeout=180,  # 增加超时时间到3分钟
        max_retries=3  # 增加重试次数
    )
    
    # 创建工具
    tools = [
        JDAnalysisTool(),
        InterviewScheduleTool(),
        KnowledgeBaseQueryTool(),
        ProgressTrackingTool()
    ]
    
    return JobSearchAgent(llm, tools) 