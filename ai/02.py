# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
import json
from datetime import  datetime
import streamlit as st

client = OpenAI(
    api_key=os.environ.get('API_KEY'),
    base_url="https://api.deepseek.com")
# 保存会话信息
def save_date():
        save_data = {
            "message": st.session_state.message,
            "name": st.session_state.name,
            "character": st.session_state.character,
            "current_time": st.session_state.current_time
        }
        if not os.path.exists('session'):
            os.mkdir('session')
        with open(f'session/{st.session_state.current_time}.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
# 加载会话列表
def load_session():
    session_list=[]
    file_list = os.listdir('session')
    for file in file_list:
        if file.endswith(".json"):
            session_list.append(file[:-5])
    session_list.sort(reverse= True)
    return session_list




# ai提示
system_prompt = '''
你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
        规则：
            1. 每次只能回复3条内的信息
            2. 禁止任何场景或状态描述性文字
            3. 匹配用户的语言
            4. 回复简短，像微信聊天一样
            5. 有需要的话可以用❤️🌸等emoji表情
            6. 用符合伴侣性格的方式对话
            7. 回复的内容, 要充分体现伴侣的性格特征
        伴侣性格：
            - %s
        你必须严格遵守上述规则来回复用户。
        '''

# 页面初始设置
st.set_page_config(
    page_title="Ai智能聊天伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items = {}
)

# 标题 logo
st.title("Ai智能聊天伴侣")
st.logo('resoures/logo.png')

# 缓存数据
if 'message' not in st.session_state:
    st.session_state.message = []
if 'name' not in st.session_state:
    st.session_state.name = ''
if 'character' not in st.session_state:
    st.session_state.character = ''
if 'current_time' not in st.session_state:
    st.session_state.current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# 显示聊天信息
st.text(f'当前会话：{st.session_state.current_time}')
for message in st.session_state.message:
    st.chat_message(message["role"]).write(message["content"])
# 侧边栏
with st.sidebar:
    st.subheader('Ai控制面板')
    if st.button('新建会话',width='stretch'):
        # 保存会话
        save_date()
        #创建新会话
        if st.session_state.message:
            st.session_state.message=[]
            st.session_state.current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            save_date()
            st.rerun()
    st.text('会话历史')
    session_list = load_session()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        # 加载会话
        with col1:
            if st.button(session,width='stretch',type='primary'if st.session_state.current_time==session else 'secondary'):
                with open(f'session/{session}.json', 'r', encoding='utf-8')as f:
                    data = json.load(f)
                    st.session_state.message = data['message']
                    st.session_state.name = data['name']
                    st.session_state.character = data['character']
                    st.session_state.current_time = session
                    st.rerun()
        # 删除会话
        with col2:
            if st.button('',width='stretch',icon='❌️',key=f'delete_{session}'):
                os.remove(f'session/{session}.json')
                if session == st.session_state.current_time:
                    st.session_state.message = []
                    st.session_state.current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    st.rerun()


    st.divider()
    st.subheader('伴侣信息')
    name = st.text_input('昵称',placeholder='请输入昵称',value=st.session_state.name)
    if name:
        st.session_state.name = name

    character = st.text_area('性格',placeholder='请输入性格',value=st.session_state.character)
    if character:
        st.session_state.character = character

# 聊天输入框
prompt = st.chat_input('你想跟我聊聊天吗')
if prompt:
    st.chat_message('user').write(prompt)
    st.session_state.message.append({"role": "user", "content": prompt})
# 调用deepseek
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt%(st.session_state.name,st.session_state.character)},
            *st.session_state.message,
        ],
        stream=True
    )
#流式输出
    box = st.empty()
    full_data = ''
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_data +=chunk.choices[0].delta.content
            box.chat_message('assistant').write(full_data)


    #保存ai返回数据
    st.session_state.message.append({"role": "assistant", "content": full_data})
    save_date()