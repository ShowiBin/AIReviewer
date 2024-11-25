import sqlite3
import schedule
import time
from datetime import datetime, timedelta
from plyer import notification
import kimi

# 通知器，在windows上这里用的是plyer，若是在安卓上，可以用其他更优的方式，如闹钟等？
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="AI复习助手",
        timeout=60  # 通知显示时间（秒）
    )

# 数据库操作类.默认不删除之前的数据
class KnowledgeDB:
    '''将知识点存储到数据库中，以便后续复习。'''
    def __init__(self, db_name="knowledge.db"):
        '''初始化数据库，如果存在该数据库则删掉'''
        
        ## 用于调试
        ## 使用时请删除 
        # import os
        # if os.path.exists(db_name):
        #     os.remove(db_name)

        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        # 创建知识点表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                date TEXT,
                                content TEXT,
                                summary TEXT)''')
        self.connection.commit()

    def add_knowledge(self, date, content, summary):
        self.cursor.execute("INSERT INTO knowledge (date, content, summary) VALUES (?, ?, ?)", (date, content, summary))
        self.connection.commit()

    def get_knowledge_by_date(self, date):
        self.cursor.execute("SELECT summary FROM knowledge WHERE date = ?", (date,))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


# chat 1 将对话内容传递给Kimi API，生成摘要
def summary_knowledge(content):
    sum_kimi = kimi.Kimi('我需要你将我接下来说的所有文本凝炼成若干个很简短的知识点')
    return sum_kimi.chat(content)
# chat 2 通过知识点生成问题 以及 相应的答案
def generate_question(content):
    gen_kimi = kimi.Kimi('我需要你用以下很简短的知识点，构思少许几个题目，来帮我快速复习这些知识点')
    q = gen_kimi.chat(content)
    v = gen_kimi.chat('同时，我需要你将这些题目的答案也给我')
    return q,v,gen_kimi.history





# 提醒存储内容
def store_knowledge(db):
    # toaster.show_toast("每日学习提醒", "请回答今天学了什么内容？", duration=10)
    show_notification("每日学习提醒", "请回答今天学了什么内容？")
    content = input("请输入今天学的内容：")  # 用于调试，实际情况可从弹窗或其他方式获取输入
    summary = summary_knowledge(content)  # 通过Kimi API生成摘要
    today_date = datetime.now().strftime("%Y-%m-%d")
    db.add_knowledge(today_date, content, summary)
    print(f"知识点已存储: {summary}")


# 复习指定日期的知识
def review_knowledge(db):
    # 根据遗忘曲线计算复习日期（例：7天前）#！！！！！！！！！！！
    review_date = (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d")## 用于调试
    # review_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    knowledge = db.get_knowledge_by_date(review_date)
    if not knowledge:
        show_notification("复习提醒", f"没有找到{review_date}的学习记录。")
        return
    show_notification("复习提醒", f"开始复习{review_date}的内容！")
    print('AI老师正在准备复习题目...')
    for summary in knowledge:
        question,answer_real,history = generate_question(f"{summary[0]}")
        print(f"问题: {question}")
        answer = input("请输入你的回答：")
        print(f"你的回答: {answer} ")
        print(f"实际答案: {answer_real}")
        print(f"知识点: {summary[0]}")
        
        # 接着是自由问答环节
            # 这样做可以接着之前的hisoty对话
        fur_kimi = kimi.Kimi()
        fur_kimi.change_hostory(history)
        print("接下来你可以自由提问，或者输入'quit'退出。")
        my_question = ''
        while my_question != 'quit':
            my_question = input("I:")
            answer = fur_kimi.chat(my_question)
            print(f"AI: {answer} ")


# 主程序入口
def main():
    db = KnowledgeDB()


    schedule.every().day.at("22:00").do(store_knowledge, db=db)  # 每天晚上10点存储内容
    schedule.every().day.at("12:30").do(review_knowledge, db=db)  # 每天zao上12.30点复习内容
    
    # schedule.every().day.at("17:04").do(store_knowledge, db=db)  # 每天晚上10点存储内容
    # schedule.every().day.at("17:05").do(review_knowledge, db=db)  # 每天zao上12.30点复习内容

    print("AI复习助手程序已启动，按Ctrl+C退出。")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序已终止。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
