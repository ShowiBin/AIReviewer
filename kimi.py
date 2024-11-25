from openai import OpenAI
 
client = OpenAI(
    api_key = "$API_KEY$",
    base_url = "https://api.moonshot.cn/v1",
)


class Kimi:
    def __init__(self,history=None):
        '''参数history用于初始化'''
        
        self.history = [
            {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。同时，你的回答要尽量保证简短！"}
        ]
        if history is not None:
            self.history.append(
                {"role": "user", "content": history}
            )
    def change_hostory(self,history):
        self.history = history
    def chat(self,query):

        history = self.history
        history.append({
            "role": "user", 
            "content": query
        })
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=history,
            temperature=0.3,
        )
        result = completion.choices[0].message.content
        history.append({
            "role": "assistant",
            "content": result
        })
        return result
 
# print(chat("地球的自转周期是多少？", history))
# print(chat("月球呢？", history))

# 需要kimi agent实现三个功能：
# 1.对话进行复习，并且总结对话内容，精简为知识点
# 2.基于知识点，生成复习题目，进行对话