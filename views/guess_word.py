import re
import streamlit as st

from utils.cache import PageCache
from utils.llm import chat_stream
from datetime import datetime

cache = PageCache('hanzi_riddle')

SYSTEM_PROMPT = '''
    你是一个专门出字谜猜谜的AI小助手，只进行字谜互动，不闲聊无关内容。全程纯文本交互，请严格遵守以下规则：
    
    一、出题规则
    1. 开场先友好打招呼，并随机出一道常见、简单、适合大众的字谜，不生僻、不低俗、不使用网络烂梗。
    2. 题目格式：“谜面”（打一字）。
    3. 每次出题必须完全随机，禁止重复使用相同题目；你需要在对话上下文中主动记录已使用过的谜语，确保同一会话内绝对不重复。
    4. 避免使用高频重复的经典老谜语，尽量选择多样化的中等常见谜语。
    
    二、【判题规则（最重要！）】
    1. 判题时，只看用户输入中的核心汉字，忽略无关内容：
        1.1. 比如用户输入“江字”“江”“jiang”，都视为答案是[江]；
        1.2. 用户输入“是江吗？”“应该是江。”，也视为答案是[江]。
    2. 核心字与正确答案完全一致 → 判为正确，回复：“太棒了！答对了！就是‘XX’字！要不要再来一题？”
    3. 核心字与正确答案不一致 → 判为错误，回复：“不对哦，再想想～ 给你个小提示：【简短线索，不泄露答案】”
    4. 用户说“不知道”→ 公布答案，先揭晓谜底和解释，再问“要不要再来一题？”
    
    三、互动流程
    1. 用户答对：夸奖 + 确认正确 + 询问“要不要再来一题？”
    2. 用户答错：告知不对 + 简单提示 + 鼓励继续猜
    3. 用户说“提示一下”：给出简短线索，不公布答案
    4. 用户说“公布答案”或“不知道”：揭晓谜底并解释 + 询问“要不要再来一题？”
    5. 用户说“换一题”“再来一题”：立即更新新字谜
    
    四、其他要求
    1. 语气轻松有趣、简洁明快，不啰嗦。
    2. 全程只围绕字谜，不回答其他问题、不聊无关话题。
    3. 不使用多余表情符号，保持简洁。
    4. 若用户答案与正确答案仅差一字或笔画，请仔细核对是否正确。
    
    请严格按以上规则回复，优先保证谜语的随机性和多样性。
'''


def _get_key() -> str:
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def _parse_answer(text: str) -> str | None:
    """从 AI 回复中提取【答案:X】标签的答案，兼容全半角冒号和空格"""
    match = re.search(r'【答案[:：]\s*(.)】', text)
    return match.group(1) if match else None


def _strip_answer_tag(text: str) -> str:
    """去掉【答案:X】标签"""
    return re.sub(r'【答案[:：]\s*.】', '', text).strip()


def _init():
    # 如果已有保存的对局，默认加载最新的一个，而非创建新会话
    if cache.get('current_session') is None:
        sessions = cache.list_saved()
        if sessions:
            _show_session(sessions[0])
            return
    cache.init({
        'messages': [],
        'score': 0,
        'round': 0,
        'current_session': _get_key(),
        'game_started': False,
        'current_answer': '',
        'wrong_count': 0,
    })


def _save_current_session():
    messages = cache.get('messages')
    if not messages:
        return
    data = {
        'score': cache.get('score'),
        'round': cache.get('round'),
        'current_session': cache.get('current_session'),
        'messages': messages,
        'game_started': cache.get('game_started'),
        'current_answer': cache.get('current_answer'),
        'wrong_count': cache.get('wrong_count'),
    }
    cache.save(cache.get('current_session'), data)


def _clear_session():
    cache.set('current_session', _get_key())
    cache.set('messages', [])
    cache.set('score', 0)
    cache.set('round', 0)
    cache.set('game_started', False)
    cache.set('current_answer', '')
    cache.set('wrong_count', 0)


def _add_session():
    _save_current_session()
    _clear_session()


def _show_session(name: str):
    data = cache.load(name)
    cache.set('score', data.get('score', 0))
    cache.set('round', data.get('round', 0))
    cache.set('current_session', data['current_session'])
    cache.set('messages', data['messages'])
    cache.set('game_started', data.get('game_started', False))
    cache.set('current_answer', data.get('current_answer', ''))
    cache.set('wrong_count', data.get('wrong_count', 0))


def _del_session(name: str):
    if cache.get('current_session') == name:
        _clear_session()
    cache.delete(name)
    st.toast(f'🗑️ 对局 {name} 已删除', icon='✅')


def render_sidebar():
    _init()
    st.subheader('🎯 谜盒控制')
    st.button('新对局', width='stretch', icon='🔄', on_click=_add_session)

    sessions = cache.list_saved()
    if sessions:
        st.text('对局历史')
        with st.container(height=200):
            for name in sessions:
                col, col2 = st.columns([5, 1])
                with col:
                    st.button(
                        name, width='stretch',
                        on_click=lambda f=name: _show_session(f),
                        key='riddle_history_' + name,
                        type='primary' if cache.get('current_session') == name else 'secondary'
                    )
                with col2:
                    st.button(
                        '', width='stretch', icon='❌',
                        on_click=lambda f=name: _del_session(f),
                        key='del_riddle_history_' + name
                    )

    st.divider()
    score = cache.get('score') or 0
    round_num = cache.get('round') or 0
    st.subheader('📊 战绩')
    st.metric('得分', f'{score} 分')
    st.metric('已出题数', f'{round_num} 题')
    if round_num > 0:
        st.metric('正确率', f'{score / round_num * 100:.0f}%')

    st.divider()
    st.caption('💡 提示：输入"跳过"可跳过当前题目')


def _stream_and_collect(response) -> str:
    """流式输出AI回复并返回完整文本，展示时隐藏答案标签"""
    response_msg = st.empty()
    full_response = ''
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            response_msg.chat_message("assistant").write(_strip_answer_tag(full_response))
    return full_response


def render_main():
    _init()
    messages = cache.get('messages')
    current_answer = cache.get('current_answer') or ''

    # 首次进入自动出题
    if not cache.get('game_started'):
        cache.set('game_started', True)
        start_msg = [{'role': 'system', 'content': SYSTEM_PROMPT},
                     {'role': 'user', 'content': '我们开始猜字谜吧！请出第一题。'}]
        response = chat_stream(start_msg)
        full_response = _stream_and_collect(response)

        answer = _parse_answer(full_response)
        if answer:
            cache.set('current_answer', answer)
            current_answer = answer

        messages.append({'role': 'user', 'content': '我们开始猜字谜吧！请出第一题。'})
        messages.append({'role': 'assistant', 'content': full_response})
        cache.set('round', 1)
        _save_current_session()
    else:
        # 回放历史消息：隐藏答案标签和系统判题指令
        for msg in messages:
            if msg['role'] == 'user' and msg['content'].startswith('[系统]'):
                continue  # 跳过内部判题指令，不展示
            if msg['role'] == 'assistant':
                st.chat_message("assistant").write(_strip_answer_tag(msg['content']))
            else:
                st.chat_message(msg['role']).write(msg['content'])

    content = st.chat_input('输入一个字，或输入"跳过"跳过当前题')
    if content:
        st.chat_message("user").write(content)
        messages.append({'role': 'user', 'content': content})

        # ===== 后端精确判题 =====
        user_input = content.strip()
        is_skip = user_input in ('跳过', '放弃', 'skip')
        is_correct = (not is_skip) and (current_answer != '') and (user_input == current_answer)

        if is_correct:
            judge_hint = f'[系统]猜对了！答案就是"{current_answer}"。请极度夸张地夸奖，然后出下一题（末尾带【答案:X】）。'
            cache.set('score', (cache.get('score') or 0) + 1)
            cache.set('wrong_count', 0)
        elif is_skip:
            judge_hint = f'[系统]用户跳过，答案是"{current_answer}"。直接揭晓答案，然后出下一题（末尾带【答案:X】）。'
            cache.set('wrong_count', 0)
        else:
            wrong_count = (cache.get('wrong_count') or 0) + 1
            cache.set('wrong_count', wrong_count)
            if wrong_count >= 2:
                # 两次没猜出来，直接揭晓答案出下一题
                judge_hint = f'[系统]用户已猜错{wrong_count}次，答案是"{current_answer}"。直接揭晓答案，然后出下一题（末尾带【答案:X】），不许废话。'
                cache.set('wrong_count', 0)
            else:
                judge_hint = f'[系统]用户猜了"{user_input}"，猜错了。给一句简短提示，不说答案，不带【答案】标签。'

        full_messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            *messages,
            {'role': 'user', 'content': judge_hint},
        ]
        response = chat_stream(full_messages)
        full_response = _stream_and_collect(response)

        # 记入消息历史
        messages.append({'role': 'user', 'content': judge_hint})
        messages.append({'role': 'assistant', 'content': full_response})

        # 如果出了新题，更新答案和轮次
        new_answer = _parse_answer(full_response)
        if new_answer:
            cache.set('current_answer', new_answer)
            cache.set('round', (cache.get('round') or 0) + 1)

        _save_current_session()

    # 答案显示放在 main 末尾，确保拿到最新值
    ans = cache.get('current_answer') or ''
    with st.sidebar:
        st.divider()
        with st.expander('🔑 查看当前答案', expanded=False, key=f'answer_reveal_{len(messages)}'):
            st.caption(ans if ans else '暂无')
