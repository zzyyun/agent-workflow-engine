"""验证 langchain 依赖安装。"""
import langchain
from langchain_core.language_models import FakeListChatModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import tool

print("langchain      :", langchain.__version__)
print("langchain-core :", __import__("langchain_core").__version__ if hasattr(__import__("langchain_core"), "__version__") else "(no __version__)")
print("FakeListChatModel:", FakeListChatModel.__name__)
print("@tool          :", tool.__name__)
print("ChatPromptTemplate:", ChatPromptTemplate.__name__)
print("Runnable       :", Runnable.__name__)

# 跑一遍 FakeListChatModel 看是否能用
fake = FakeListChatModel(responses=["hello"])
result = fake.invoke("hi")
print("FakeListChatModel test:", result.content)
