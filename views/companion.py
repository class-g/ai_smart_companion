import streamlit as st

from utils.cache import PageCache
from utils.llm import chat_stream
from utils.image import show_gif
from datetime import datetime

cache = PageCache('companion')

SYSTEM_PROMPT = '''
你叫 %s，现在是用户的真实伴侣，请完全代入伴侣角色。
规则：
    1. 每次只回1条消息
    2. 禁止任何场景或状态描述性文字
    3. 匹配用户的语言
    4. 回复简短，像微信聊天一样
    5. 需要的时候可以用❤️🌸等emoji表情
    6. 用符合伴侣性格的方式对话
    7. 回复的内容，要充分体现伴侣的性格特征
    8. emoji要像真人一样自然穿插在句子中间，不要刻意堆砌在句尾
伴侣性格：
    - %s
你必须严格遵守上述规则来回复用户。
'''


def _get_key() -> str:
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def _init():
    # 如果已有保存的会话，默认加载最新的一个，而非创建新会话
    if cache.get('current_session') is None:
        sessions = cache.list_saved()
        if sessions:
            _show_session(sessions[0])
            return
    cache.init({
        'messages': [],
        'nick_name': '小甜甜',
        'nature': '活泼可爱好看的女孩',
        'current_session': _get_key(),
    })


def _save_current_session():
    messages = cache.get('messages')
    if not messages:
        return
    data = {
        'nick_name': cache.get('nick_name'),
        'nature': cache.get('nature'),
        'current_session': cache.get('current_session'),
        'messages': messages,
    }
    cache.save(cache.get('current_session'), data)


def _clear_session():
    cache.set('current_session', _get_key())
    cache.set('messages', [])


def _add_session():
    _save_current_session()
    _clear_session()


def _show_session(name: str):
    data = cache.load(name)
    cache.set('nick_name', data['nick_name'])
    cache.set('nature', data['nature'])
    cache.set('current_session', data['current_session'])
    cache.set('messages', data['messages'])


def _del_session(name: str):
    if cache.get('current_session') == name:
        _clear_session()
    cache.delete(name)
    st.toast(f'🗑️ 会话 {name} 已删除', icon='✅')


def render_sidebar():
    _init()
    st.subheader('AI控制面板')
    st.button('新建会话', width='stretch', icon='📝', on_click=_add_session)

    sessions = cache.list_saved()
    if sessions:
        st.text('会话历史')
        with st.container(height=200):
            for name in sessions:
                col, col2 = st.columns([5, 1])
                with col:
                    st.button(
                        name, width='stretch',
                        on_click=lambda f=name: _show_session(f),
                        key='history_' + name,
                        type='primary' if cache.get('current_session') == name else 'secondary'
                    )
                with col2:
                    st.button(
                        '', width='stretch', icon='❌',
                        on_click=lambda f=name: _del_session(f),
                        key='del_history_' + name
                    )

    st.divider()
    st.subheader('伴侣信息')
    nick_name = st.text_input('昵称', placeholder='请输入昵称', value=cache.get('nick_name'))
    if nick_name:
        cache.set('nick_name', nick_name)
    nature = st.text_area('性格', placeholder='请输入性格', value=cache.get('nature'))
    if nature:
        cache.set('nature', nature)


def render_main():
    _init()
    messages = cache.get('messages')
    for msg in messages:
        st.chat_message(msg['role']).write(msg['content'])

    content = st.chat_input("请输入你想要我回复的内容")
    if content:
        st.chat_message("user").write(content)
        messages.append({'role': 'user', 'content': content})

        full_messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT % (cache.get('nick_name'), cache.get('nature'))},
            *messages
        ]
        response = chat_stream(full_messages)

        response_msg = st.empty()
        full_response = ''
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_msg.chat_message("assistant").write(full_response)

        messages.append({'role': 'assistant', 'content': full_response})
        _save_current_session()
