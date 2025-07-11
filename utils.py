from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Optional
import os
from datetime import date

def init_moonshot_llm(temperature: float = 0.7) -> ChatOpenAI:
    """初始化 Moonshot API 客户端"""
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        raise ValueError("请设置 MOONSHOT_API_KEY 环境变量")
    
    return ChatOpenAI(
        temperature=temperature,
        model_name="moonshot-v1-8k",
        openai_api_key=api_key,
        openai_api_base="https://api.moonshot.cn/v1",
        max_tokens=4096  # 提升最大输出长度，解决内容截断问题
    )

def analyze_job_description(
    prompt_template: PromptTemplate,
    jd_content: str,
    resume_content: str,
    temperature: float = 0.7
) -> tuple[Optional[str], Optional[str]]:
    """
    分析职位描述和简历内容
    (已更新为 LangChain 最新语法)
    """
    try:
        llm = init_moonshot_llm(temperature)
        # 使用 LangChain Expression Language (LCEL) 的新方法
        chain = prompt_template | llm
        
        response = chain.invoke({
            "jd_content": jd_content,
            "resume_content": resume_content
        })
        
        # response 对象现在是 AIMessage，需要获取其 content
        return response.content, None
        
    except Exception as e:
        error_msg = f"分析过程中出现错误: {str(e)}"
        return None, error_msg

def generate_interview_schedule(
    prompt_template: PromptTemplate,
    interview_date: date,
    jd_analysis_result: str,  # 新增参数
    temperature: float = 0.7
) -> tuple[Optional[str], Optional[str]]:
    """根据面试日期和JD分析报告，生成个性化的准备计划"""
    try:
        today = date.today()
        days_diff = (interview_date - today).days
        
        if days_diff < 0:
            return None, "面试日期不能早于今天。"
        if days_diff == 0:
            return "就是今天！祝你面试顺利，发挥出最佳水平！", None

        llm = init_moonshot_llm(temperature)
        chain = prompt_template | llm

        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        
        response = chain.invoke({
            "jd_analysis_result": jd_analysis_result,  # 传入新参数
            "days_to_interview": days_diff + 1,
            "today_date": today.strftime("%Y年%m月%d日") + " " + weekdays[today.weekday()],
            "interview_date": interview_date.strftime("%Y年%m月%d日") + " " + weekdays[interview_date.weekday()]
        })

        return response.content, None

    except Exception as e:
        error_msg = f"任务生成过程中出现错误: {str(e)}"
        return None, error_msg

def validate_inputs(jd_content: str, resume_content: str) -> tuple[bool, str]:
    """验证输入内容
    
    Args:
        jd_content: 职位描述内容
        resume_content: 简历内容
        
    Returns:
        tuple[bool, str]: (是否有效, 错误信息)
    """
    if not jd_content.strip():
        return False, "请填写职位描述(JD)内容"
    
    if not resume_content.strip():
        return False, "请填写简历内容"
    
    if len(jd_content) < 50:
        return False, "职位描述内容过短，请提供更详细的信息"
    
    if len(resume_content) < 50:
        return False, "简历内容过短，请提供更详细的信息"
    
    return True, "" 