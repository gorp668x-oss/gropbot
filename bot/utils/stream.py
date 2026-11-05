import asyncio
import re
import secrets

import httpx

_TAG = re.compile(r"(<[^>]+>)")


def _prefixes(text: str):
    """پیشوندهای تدریجی متن HTML (کلمه به کلمه)؛ تگ‌های باز را می‌بندد."""
    out, acc, stack = [], "", []
    for tok in _TAG.split(text):
        if _TAG.fullmatch(tok):
            acc += tok
            name = re.match(r"</?\s*([a-zA-Z0-9-]+)", tok).group(1)
            if tok.startswith("</"):
                if stack and stack[-1] == name:
                    stack.pop()
            else:
                stack.append(name)
            continue
        for piece in re.findall(r"\s+|\S+", tok):
            acc += piece
            if not piece.isspace():
                out.append(acc + "".join(f"</{t}>" for t in reversed(stack)))
    out.append(acc)
    return out


async def stream_draft(token: str, chat_id: int, text: str,
                       delay: float = 0.15, max_steps: int = 20) -> bool:
    """متن را با sendMessageDraft تدریجی نشان می‌دهد. اگر خطا داد False برمی‌گرداند."""
    steps = _prefixes(text)
    if len(steps) > max_steps:
        k = len(steps) / max_steps
        steps = [steps[int(i * k)] for i in range(max_steps)] + [steps[-1]]

    draft_id = secrets.randbelow(2**31 - 1) + 1
    url = f"https://api.telegram.org/bot{token}/sendMessageDraft"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            for part in steps:
                r = await client.post(url, json={
                    "chat_id": chat_id,
                    "draft_id": draft_id,
                    "text": part,
                    "parse_mode": "HTML",
                })
                if r.status_code != 200 or not r.json().get("ok"):
                    print(f"sendMessageDraft failed: {r.text}")
                    return False
                await asyncio.sleep(delay)
        return True
    except Exception as e:
        print(f"sendMessageDraft error: {e}")
        return False