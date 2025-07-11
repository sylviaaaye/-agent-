from typing import Optional
import os

def validate_inputs(jd_content: str, resume_content: str) -> tuple[bool, str]:
    """验证输入内容"""
    if not jd_content.strip():
        return False, "请填写职位描述(JD)内容"
    
    if not resume_content.strip():
        return False, "请填写简历内容"
    
    if len(jd_content) < 50:
        return False, "职位描述内容过短，请提供更详细的信息"
    
    if len(resume_content) < 50:
        return False, "简历内容过短，请提供更详细的信息"
    
    return True, ""

def analyze_job_description(
    prompt_template: any,
    jd_content: str,
    resume_content: str,
    temperature: float = 0.7
) -> tuple[Optional[str], Optional[str]]:
    """简化版分析函数，暂时返回测试结果"""
    try:
        # 暂时返回测试结果
        result = f"""
# 测试分析结果

## 岗位匹配度分析
- 技能匹配度：85%
- 这是一个测试结果

## 推荐准备方向
- 准备相关技术栈
- 复习算法题

JD长度: {len(jd_content)}
简历长度: {len(resume_content)}
温度参数: {temperature}
"""
        return result, None
        
    except Exception as e:
        error_msg = f"分析过程中出现错误: {str(e)}"
        return None, error_msg 