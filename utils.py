from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from typing import Optional, List
import os
from datetime import date
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
# --- 导入新的 prompt ---
from prompts import jd_analysis_prompt, jd_analysis_prompt_legacy

# === 全局RAG链缓存 ===
_rag_chain_cache = None
_retriever_cache = None

def load_knowledge_base(kb_path: str) -> List[Document]:
    """
    加载知识库文件（支持 .pdf 和 .md）
    
    Args:
        kb_path: 知识库目录路径
        
    Returns:
        加载的文档列表
    """
    documents = []
    if not os.path.isdir(kb_path):
        print(f"警告: 知识库目录 '{kb_path}' 不存在。")
        return documents

    for filename in os.listdir(kb_path):
        file_path = os.path.join(kb_path, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif filename.endswith(".md"):
            loader = UnstructuredMarkdownLoader(file_path)
            documents.extend(loader.load())
    
    print(f"成功从 '{kb_path}' 加载了 {len(documents)} 个文档片段。")
    return documents

def create_rag_chain(prompt_template: ChatPromptTemplate, temperature: float = 0.7):
    """
    创建并返回一个完整的 RAG (Retrieval-Augmented Generation) 链。
    使用全局缓存避免重复创建，解决Agent模式下的API限流问题。
    """
    global _rag_chain_cache, _retriever_cache
    
    # 检查缓存
    if _rag_chain_cache is not None and _retriever_cache is not None:
        print("✅ 使用缓存的RAG链，避免重复向量化")
        return _rag_chain_cache, _retriever_cache
    
    print("🔄 首次创建RAG链...")
    
    # 1. 加载知识库文档
    kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base')
    documents = load_knowledge_base(kb_path)
    
    if not documents:
        print("知识库为空，无法创建 RAG 链。")
        return None, None # 返回 None 表示无法创建

    # 2. 文本分割
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    # 3. 创建 Embedding 模型
    # 使用 OpenAI 专门的 embedding 模型，效果和兼容性更好
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        # 如果没有找到 OpenAI API Key，我们可以打印一个更友好的错误提示，而不是让程序崩溃
        print("错误: 未找到 OPENAI_API_KEY 环境变量。RAG 功能需要此密钥。")
        print("将回退到无知识库的普通分析模式。")
        return None, None # 返回 None 表示无法创建 RAG 链

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=openai_api_key
    )

    # 4. 创建向量数据库和检索器
    # 采用分批处理的方式，防止一次性发送过多token导致API错误
    if not split_docs:
        print("警告: 知识库为空或分割后无内容。")
        return None, None
        
    print("正在分批为知识库文档创建向量索引...")
    # 先用第一个文档块初始化 FAISS 索引
    vector_store = FAISS.from_documents([split_docs[0]], embeddings)
    
    # 定义一个合理的批处理大小
    batch_size = 32 
    
    # 循环处理剩余的文档块
    for i in range(1, len(split_docs), batch_size):
        batch = split_docs[i:i + batch_size]
        if batch:
            vector_store.add_documents(batch)
            print(f"  - 已处理批次 {i // batch_size + 1}")
    
    print("向量索引创建完成！")
    retriever = vector_store.as_retriever()

    # 5. 创建并返回 RAG 链
    llm = init_moonshot_llm(temperature)
    
    # 这个链负责将检索到的文档"塞入"提示词
    question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
    
    # 这个链负责"检索"->"塞入"->"生成"的完整流程
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    # 缓存结果
    _rag_chain_cache = rag_chain
    _retriever_cache = retriever
    
    print("✅ RAG链创建完成并已缓存")
    return rag_chain, retriever # 同时返回检索器，方便调试

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
        max_tokens=4096,  # 提升最大输出长度，解决内容截断问题
        request_timeout=120,  # 增加超时时间到2分钟
        max_retries=5  # 增加重试次数
    )

def analyze_job_description(
    jd_content: str,
    resume_content: str,
    temperature: float = 0.7
) -> tuple[Optional[str], Optional[str]]:
    """
    分析职位描述和简历内容
    (已更新为 LangChain 最新语法，并集成 RAG 功能)
    """
    try:
        # 减少延迟，因为现在有缓存机制
        import time
        time.sleep(1)  # 从5秒减少到1秒
        
        # 1. 尝试创建 RAG 链（现在有缓存，不会重复向量化）
        rag_chain, retriever = create_rag_chain(jd_analysis_prompt, temperature)
        
        # 2. 如果 RAG 链创建成功，则使用 RAG 流程
        if rag_chain:
            print("正在使用 RAG 流程进行分析...")
            # 将JD作为核心输入，用于检索知识库
            input_dict = {
                "input": jd_content, 
                "jd_content": jd_content,
                "resume_content": resume_content
            }
            response = rag_chain.invoke(input_dict)
            return response.get("answer"), None
            
        # 3. 如果 RAG 链创建失败（如知识库为空），则回退到普通流程
        else:
            print("知识库为空或加载失败，回退到普通分析流程...")
            llm = init_moonshot_llm(temperature)
            chain = jd_analysis_prompt_legacy | llm
            
            response = chain.invoke({
                "jd_content": jd_content,
                "resume_content": resume_content
            })
            
            return response.content, None
        
    except Exception as e:
        error_msg = f"分析过程中出现错误: {str(e)}"
        if "429" in str(e) or "rate_limit" in str(e):
            error_msg += "\n\n💡 提示：API限流，请等待1-2分钟后重试"
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