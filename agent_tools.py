import time
import json
from typing import Any, Dict, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from utils import analyze_job_description, generate_interview_schedule
from prompts import task_generation_prompt
import os
from datetime import date

class JDAnalysisInput(BaseModel):
    jd_content: str = Field(description="职位描述内容")
    resume_content: str = Field(description="简历内容")

class InterviewScheduleInput(BaseModel):
    jd_analysis_result: str = Field(description="JD分析结果")
    interview_date: str = Field(description="面试日期，格式：YYYY-MM-DD")

class KnowledgeQueryInput(BaseModel):
    query: str = Field(description="知识库查询内容")

class ProgressInput(BaseModel):
    current_progress: str = Field(description="当前进度描述")

class JDAnalysisTool(BaseTool):
    name: str = "jd_analysis"
    description: str = "分析职位描述和简历的匹配度，生成详细的面试准备建议"
    args_schema: type = JDAnalysisInput
    
    def _run(self, **kwargs) -> str:
        """执行JD分析 - 使用**kwargs来处理各种输入格式"""
        try:
            # 减少延迟，因为utils.py中已经有缓存机制
            time.sleep(0.5)
            
            # 处理不同的输入格式
            if 'jd_content' in kwargs and 'resume_content' in kwargs:
                jd_content = kwargs['jd_content']
                resume_content = kwargs['resume_content']
            else:
                # 如果参数不完整，返回错误信息
                return "❌ 参数错误：需要提供 jd_content 和 resume_content 参数"
            
            result, error = analyze_job_description(jd_content, resume_content)
            if error:
                # 改进错误处理
                if "429" in str(error) or "rate_limit" in str(error):
                    return "⚠️ API限流中，建议：\n1. 等待2-3分钟后重试\n2. 或使用离线测试模式\n3. 或切换到传统模式"
                return f"分析失败：{error}"
            return result
        except Exception as e:
            return f"工具执行错误：{str(e)}"

class InterviewScheduleTool(BaseTool):
    name: str = "interview_schedule"
    description: str = "根据JD分析结果和面试日期，生成个性化的面试准备计划"
    args_schema: type = InterviewScheduleInput
    
    def _run(self, **kwargs) -> str:
        """生成面试计划 - 使用**kwargs来处理各种输入格式"""
        try:
            # 减少延迟
            time.sleep(0.5)
            
            # 处理不同的输入格式
            if 'jd_analysis_result' in kwargs and 'interview_date' in kwargs:
                jd_analysis_result = kwargs['jd_analysis_result']
                interview_date_str = kwargs['interview_date']
            else:
                return "❌ 参数错误：需要提供 jd_analysis_result 和 interview_date 参数"
            
            # 解析日期
            interview_date_obj = date.fromisoformat(interview_date_str)
            
            result, error = generate_interview_schedule(
                task_generation_prompt,
                interview_date_obj,
                jd_analysis_result
            )
            
            if error:
                # 改进错误处理
                if "429" in str(error) or "rate_limit" in str(error):
                    return "⚠️ API限流中，建议：\n1. 等待2-3分钟后重试\n2. 或使用离线测试模式"
                return f"计划生成失败：{error}"
            return result
        except Exception as e:
            return f"工具执行错误：{str(e)}"

class KnowledgeBaseQueryTool(BaseTool):
    name: str = "knowledge_base_query"
    description: str = "查询知识库，获取相关的学习资料和技术文档"
    args_schema: type = KnowledgeQueryInput
    
    def _run(self, **kwargs) -> str:
        """查询知识库 - 使用**kwargs来处理各种输入格式"""
        try:
            # 知识库查询不需要API调用，几乎无延迟
            time.sleep(0.1)
            
            # 处理不同的输入格式
            if 'query' in kwargs:
                query = kwargs['query']
            else:
                return "❌ 参数错误：需要提供 query 参数"
            
            # 增强的知识库查询结果
            knowledge_results = {
                "机器学习": """📚 机器学习学习资源：
1. 《统计学习方法》- 李航 ⭐⭐⭐⭐⭐
2. 《机器学习》- 周志华 ⭐⭐⭐⭐⭐  
3. Coursera机器学习课程 - Andrew Ng ⭐⭐⭐⭐
4. 实战项目：Kaggle竞赛参与
5. 重点算法：决策树、SVM、随机森林、梯度提升""",
                
                "深度学习": """📚 深度学习学习资源：
1. 《深度学习》- Goodfellow ⭐⭐⭐⭐⭐
2. CS231n课程 - Stanford ⭐⭐⭐⭐⭐
3. PyTorch官方教程 ⭐⭐⭐⭐
4. 实战项目：图像分类、NLP任务
5. 重点框架：PyTorch、TensorFlow""",
                
                "算法": """📚 算法面试准备资源：
1. 《算法导论》- CLRS ⭐⭐⭐⭐⭐
2. LeetCode刷题（按标签分类）⭐⭐⭐⭐⭐
3. 《编程珠玑》- Jon Bentley ⭐⭐⭐⭐
4. 重点题型：动态规划、二分查找、图论、贪心
5. 面试策略：白板编程、时间复杂度分析""",
                
                "系统设计": """📚 系统设计面试资源：
1. 《设计数据密集型应用》- Martin Kleppmann ⭐⭐⭐⭐⭐
2. 《系统设计面试指南》⭐⭐⭐⭐
3. 高并发系统设计案例 ⭐⭐⭐⭐
4. 重点概念：负载均衡、缓存、数据库分片、微服务
5. 实战案例：设计Twitter、设计Uber、设计聊天系统""",
                
                "Python": """📚 Python技术栈资源：
1. 《流畅的Python》- Luciano Ramalho ⭐⭐⭐⭐⭐
2. Python官方文档 ⭐⭐⭐⭐⭐
3. 《Effective Python》⭐⭐⭐⭐
4. 重点知识：装饰器、生成器、异步编程、内存管理
5. 框架学习：Django、Flask、FastAPI""",
                
                "数据结构": """📚 数据结构学习资源：
1. 数组、链表、栈、队列基础 ⭐⭐⭐⭐⭐
2. 树结构：二叉树、平衡树、堆 ⭐⭐⭐⭐⭐
3. 图论：DFS、BFS、最短路径 ⭐⭐⭐⭐
4. 哈希表和集合 ⭐⭐⭐⭐⭐
5. 实现技巧：递归、迭代、空间优化"""
            }
            
            # 智能关键词匹配
            for keyword, content in knowledge_results.items():
                if keyword in query or keyword.lower() in query.lower():
                    return f"🎯 知识库查询结果 - {keyword}：\n\n{content}"
            
            # 通用查询结果
            return """🎯 知识库查询结果：

📚 通用学习资源推荐：
1. 📖 技术博客：Medium、知乎、CSDN
2. 🎓 在线课程：Coursera、edX、Udacity  
3. 💻 开源项目：GitHub热门项目实践
4. 📝 面试题库：LeetCode、牛客网、力扣
5. 📊 实战项目：Kaggle、开源贡献

💡 学习建议：
- 理论与实践结合
- 定期总结复盘
- 参与技术社区讨论
- 构建个人项目作品集"""
        except Exception as e:
            return f"知识库查询错误：{str(e)}"

class ProgressTrackingTool(BaseTool):
    name: str = "progress_tracking"
    description: str = "跟踪和评估学习进度，提供调整建议"
    args_schema: type = ProgressInput
    
    def _run(self, **kwargs) -> str:
        """跟踪进度 - 使用**kwargs来处理各种输入格式"""
        try:
            # 进度跟踪不需要API调用
            time.sleep(0.1)
            
            # 处理不同的输入格式
            if 'current_progress' in kwargs:
                current_progress = kwargs['current_progress']
            else:
                return "❌ 参数错误：需要提供 current_progress 参数"
            
            return f"""📊 进度跟踪与建议：

📈 当前进度分析：
{current_progress}

🎯 优化建议：
1. ✅ 每日学习目标制定与跟踪
2. 📝 定期知识点总结和复习 
3. 💻 理论学习与代码实践并重
4. 🗣️ 模拟面试和技术交流
5. 📊 学习效果量化评估

⏰ 时间管理建议：
- 高效时段：专注核心算法和项目
- 碎片时间：复习理论知识和八股文
- 休息调节：保持学习节奏，避免疲劳

🔄 调整策略：
- 根据薄弱环节调整学习重点
- 及时反馈和调整学习方法
- 保持积极心态和学习动力"""
        except Exception as e:
            return f"进度跟踪错误：{str(e)}"

def get_agent_tools():
    """获取所有Agent工具"""
    return [
        JDAnalysisTool(),
        InterviewScheduleTool(),
        KnowledgeBaseQueryTool(),
        ProgressTrackingTool()
    ] 