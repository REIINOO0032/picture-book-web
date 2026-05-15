from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import requests
import json
import sqlite3
import uuid
from datetime import datetime
import time
from urllib.parse import quote
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 用户表（直接包含 total_earnings）
    c.execute('''
    CREATE TABLE IF NOT EXISTS user (
        user_id VARCHAR(32) PRIMARY KEY,
        phone VARCHAR(20) NOT NULL UNIQUE,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(64) NOT NULL,
        is_vip TINYINT(1) DEFAULT 0,
        create_time DATETIME,
        update_time DATETIME,
        total_earnings DECIMAL(10,2) DEFAULT 0
    )''')

    # 绘本主表
    c.execute('''
    CREATE TABLE IF NOT EXISTS book (
        book_id VARCHAR(32) PRIMARY KEY,
        user_id VARCHAR(32) DEFAULT 'default_user',
        title VARCHAR(50),
        page_count INT,
        create_time DATETIME,
        click_count INT DEFAULT 0,
        is_vip_only TINYINT(1) DEFAULT 0
    )''')

    # 绘本分页表
    c.execute('''
    CREATE TABLE IF NOT EXISTS book_page (
        page_id VARCHAR(32) PRIMARY KEY,
        book_id VARCHAR(32),
        page_num INT,
        content TEXT,
        image_url TEXT
    )''')

    # 会员订阅表
    c.execute('''
    CREATE TABLE IF NOT EXISTS vip_subscribe (
        order_id VARCHAR(32) PRIMARY KEY,
        user_id VARCHAR(32),
        level INT DEFAULT 1,
        start_time DATETIME,
        expire_time DATETIME,
        status TINYINT(1) DEFAULT 0
    )''')

    # 系统日志表
    c.execute('''
    CREATE TABLE IF NOT EXISTS system_log (
        log_id VARCHAR(32) PRIMARY KEY,
        user_id VARCHAR(32),
        operation VARCHAR(50),
        create_time DATETIME,
        result TINYINT(1)
    )''')

    # 收益明细表
    c.execute('''
    CREATE TABLE IF NOT EXISTS earnings (
        earning_id VARCHAR(32) PRIMARY KEY,
        user_id VARCHAR(32) NOT NULL,
        book_id VARCHAR(32),
        type VARCHAR(20) NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        source_user_id VARCHAR(32),
        create_time DATETIME NOT NULL
    )''')

    conn.commit()
    conn.close()

# 执行初始化
init_db()

def get_db():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ============================
# DeepSeek + 阿里云百炼配置
# ============================

DEEPSEEK_API_KEY = "sk-cd25ec387d154f4b9b11e31aa2234b07"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DASHSCOPE_API_KEY = "sk-b5d6e9fc451d4cbea1f9441ac7950969"

# ============================
# 故事生成
# ============================

def deepseek_generate_story(topic: str, page_count: int, outline: str = "", character_desc: str = "") -> dict:
    """使用DeepSeek生成绘本故事"""
    
    character_info = ""
    if character_desc:
        character_info = f"主角形象：{character_desc}"
    
    prompt = f"""请根据我提供的主题和故事梗概，创作一个 {page_count} 页的儿童绘本故事。

【我的输入】
主题：{topic}
故事梗概：{outline if outline else "（未提供，请根据主题自由创作）"}
{character_info}

【创作要求】
1. 内容扩充：请基于我的故事梗概，保留核心情节和角色，用更丰富、更有趣的细节来填充故事内容。
2. 语言风格：使用儿童友好、简单温暖、充满童趣的语言。
3. 分页要求：严格按照 {page_count} 页进行划分，每页内容为 1～2 句话，20～35 字。
4. 结构完整：确保故事有清晰的开头、中间和结尾。

【输出格式】
请按照以下JSON格式输出：
{{
    "title": "{topic}",
    "pages": [
        {{"text": "第1页内容"}},
        {{"text": "第2页内容"}}
    ]
}}

请开始创作："""
    
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "response_format": {"type": "json_object"}
        }
        
        resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=45)
        
        if resp.status_code != 200:
            print(f"DeepSeek调用失败: {resp.text}")
            return generate_fallback_story(topic, page_count)
        
        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        story_data = json.loads(content)
        
        if len(story_data["pages"]) != page_count:
            while len(story_data["pages"]) < page_count:
                story_data["pages"].append({"text": f"{topic}的一天真快乐！"})
            story_data["pages"] = story_data["pages"][:page_count]
        
        return story_data
        
    except Exception as e:
        print(f"DeepSeek生成失败: {e}")
        return generate_fallback_story(topic, page_count)


def generate_fallback_story(topic: str, page_count: int) -> dict:
    """兜底：手动生成简单故事"""
    pages = []
    for i in range(page_count):
        pages.append({"text": f"第{i+1}页：可爱的{topic}在快乐地玩耍"})
    
    return {
        "title": f"{topic}的小故事",
        "pages": pages
    }


# ============================
# 阿里云百炼图片生成
# ============================

def tongyi_generate_image(text: str, seed: int = None) -> str:
    """使用阿里云百炼通义万相生成儿童绘本图片"""
    import time
    import requests
    
    try:
        prompt = f"""
Beatrix Potter style, English countryside watercolor illustration, 
delicate colored pencil details, soft pastoral colors, 
cute anthropomorphic animals wearing tiny vintage clothes, 
gentle lighting, botanical garden background, 
hand-drawn texture, nostalgic storybook charm, 
high quality, 4K, {text}
"""
        create_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        
        headers = {
            "X-DashScope-Async": "enable",
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "wanx-v1",
            "input": {"prompt": prompt},
            "parameters": {"size": "1024*1024", "n": 1}
        }
        
        if seed is not None:
            payload["parameters"]["seed"] = seed
        
        print(f"🎨 正在生成图片: {text[:30]}...")
        
        submit_resp = requests.post(create_url, headers=headers, json=payload, timeout=60)
        
        if submit_resp.status_code != 200:
            print(f"❌ 提交任务失败: {submit_resp.text}")
            return fallback_image(seed)
        
        result = submit_resp.json()
        task_id = result.get("output", {}).get("task_id")
        
        if not task_id:
            print(f"❌ 未获取到 task_id: {result}")
            return fallback_image(seed)
        
        print(f"📝 任务ID: {task_id}")
        
        query_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        
        for i in range(40):
            time.sleep(3)
            try:
                query_resp = requests.get(query_url, headers={"Authorization": f"Bearer {DASHSCOPE_API_KEY}"}, timeout=30)
                query_result = query_resp.json()
            except Exception as e:
                print(f"⏳ 查询异常 ({i+1}/40): {e}")
                continue
            
            status = query_result.get("output", {}).get("task_status")
            print(f"⏳ 查询状态 ({i+1}/40): {status}")
            
            if status == "SUCCEEDED":
                results = query_result.get("output", {}).get("results", [])
                if results and len(results) > 0:
                    image_url = results[0].get("url", "")
                    if image_url:
                        print(f"✅ 图片生成成功")
                        return image_url
                return fallback_image(seed)
            elif status == "FAILED":
                print(f"❌ 生成失败")
                return fallback_image(seed)
        
        return fallback_image(seed)
        
    except Exception as e:
        print(f"❌ 生成异常: {e}")
        return fallback_image(seed)


def fallback_image(seed: int = None) -> str:
    """备用图片"""
    import random
    final_seed = seed if seed is not None else random.randint(1, 10000)
    return f"https://picsum.photos/1024/1024?random={final_seed}"


def pollinations_generate_image(text: str, seed: int = None) -> str:
    """生成图片"""
    return tongyi_generate_image(text, seed)


# ============================
# 绘本生成接口
# ============================

@app.post("/generate-book")
def generate_book(data: dict, db: sqlite3.Connection = Depends(get_db)):
    topic = data.get("topic", "小动物")
    page_count = data.get("pageCount", 6)
    user_id = data.get("userId", "default_user")
    outline = data.get("outline", "")
    character_desc = data.get("character_desc", "")
    is_vip_only = data.get("is_vip_only", False)
    
    # 生成故事
    story_data = deepseek_generate_story(
        topic=topic,
        page_count=page_count,
        outline=outline,
        character_desc=character_desc
    )
    
    # 固定 seed
    fixed_seed = hash(topic) % 10000
    
    for idx, page in enumerate(story_data["pages"]):
        text = page.get("text", "")
        seed = fixed_seed + idx
        page["image"] = pollinations_generate_image(text, seed=seed)
    
    # 保存到数据库
    book_id = str(uuid.uuid4())
    c = db.cursor()
    c.execute('''INSERT INTO book
        (book_id, user_id, title, page_count, create_time, click_count, is_vip_only)
        VALUES (?,?,?,?,?,?,?)''',
        (book_id, user_id, story_data["title"], page_count, datetime.now(), 0, 1 if is_vip_only else 0)
    )
    
    for idx, page in enumerate(story_data["pages"]):
        page_id = str(uuid.uuid4())
        c.execute('''INSERT INTO book_page
            (page_id, book_id, page_num, content, image_url)
            VALUES (?,?,?,?,?)''',
            (page_id, book_id, idx+1, page["text"], page["image"])
        )
    
    db.commit()
    
    return {
        "bookId": book_id,
        "title": story_data["title"],
        "pages": story_data["pages"]
    }


@app.post("/refresh-image")
def refresh_image(data: dict):
    text = data.get("text", "")
    img = pollinations_generate_image(text)
    return {"image": img}


@app.post("/save-book-from-editor")
def save_book_from_editor(data: dict, db: sqlite3.Connection = Depends(get_db)):
    """从编辑器保存绘本到数据库"""
    title = data.get("title")
    pages = data.get("pages", [])
    user_id = data.get("userId", "default_user")
    
    book_id = str(uuid.uuid4())
    c = db.cursor()
    c.execute('''INSERT INTO book
        (book_id, user_id, title, page_count, create_time)
        VALUES (?,?,?,?,?)''',
        (book_id, user_id, title, len(pages), datetime.now())
    )
    
    for idx, page in enumerate(pages):
        page_id = str(uuid.uuid4())
        c.execute('''INSERT INTO book_page
            (page_id, book_id, page_num, content, image_url)
            VALUES (?,?,?,?,?)''',
            (page_id, book_id, idx+1, page.get("text"), page.get("image"))
        )
    
    db.commit()
    return {"bookId": book_id}


# ============================
# 绘本阅读相关接口
# ============================

@app.get("/book/{book_id}")
def get_book(book_id: str, userId: str = None, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT * FROM book WHERE book_id=?", (book_id,))
    book = c.fetchone()
    if not book:
        raise HTTPException(status_code=404, detail="绘本不存在")
    
    # 会员权限检查
    if book["is_vip_only"] == 1:
        if not userId:
            raise HTTPException(status_code=401, detail="请先登录")
        c.execute("SELECT is_vip FROM user WHERE user_id=?", (userId,))
        user = c.fetchone()
        if not user or user["is_vip"] != 1:
            raise HTTPException(status_code=403, detail="会员专享绘本，请开通会员")
    
    c.execute("SELECT page_id, page_num, content, image_url FROM book_page WHERE book_id=? ORDER BY page_num", (book_id,))
    pages = [dict(row) for row in c.fetchall()]
    
    return {
        "bookId": book["book_id"],
        "title": book["title"],
        "pages": pages
    }


@app.post("/book/update-title")
def update_book_title(data: dict, db: sqlite3.Connection = Depends(get_db)):
    book_id = data.get("bookId")
    title = data.get("title")
    
    c = db.cursor()
    c.execute("UPDATE book SET title=? WHERE book_id=?", (title, book_id))
    db.commit()
    return {"code": 200, "msg": "标题更新成功"}


@app.post("/book/update-page")
def update_page_content(data: dict, db: sqlite3.Connection = Depends(get_db)):
    page_id = data.get("pageId")
    new_text = data.get("text")
    
    c = db.cursor()
    c.execute("UPDATE book_page SET content=? WHERE page_id=?", (new_text, page_id))
    db.commit()
    return {"code": 200, "msg": "保存成功"}


@app.post("/book/delete/{book_id}")
def delete_book(book_id: str, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("DELETE FROM book_page WHERE book_id=?", (book_id,))
    c.execute("DELETE FROM book WHERE book_id=?", (book_id,))
    db.commit()
    return {"code": 200, "msg": "删除成功"}


# ============================
# 绘本推荐接口
# ============================

@app.get("/books/recommend")
def get_recommend_books(userId: str = None, db: sqlite3.Connection = Depends(get_db)):
    """获取推荐绘本：根据用户会员状态显示"""
    c = db.cursor()
    
    # 获取用户会员状态
    is_vip = False
    if userId:
        c.execute("SELECT is_vip FROM user WHERE user_id=?", (userId,))
        user = c.fetchone()
        is_vip = user["is_vip"] if user else False
    
    # 非VIP用户只能看免费绘本
    vip_filter = "" if is_vip else "WHERE is_vip_only = 0"
    
    # 获取点击量最多的3本
    c.execute(f"""
        SELECT book_id, title, page_count, create_time, user_id, click_count, is_vip_only
        FROM book {vip_filter}
        ORDER BY click_count DESC LIMIT 3
    """)
    top_books = [dict(row) for row in c.fetchall()]
    
    # 获取最新1本
    top_ids = [b["book_id"] for b in top_books]
    if top_ids:
        placeholders = ",".join(["?"] * len(top_ids))
        extra_filter = "" if is_vip else "AND is_vip_only = 0"
        c.execute(f"""
            SELECT book_id, title, page_count, create_time, user_id, click_count, is_vip_only
            FROM book 
            WHERE book_id NOT IN ({placeholders}) {extra_filter}
            ORDER BY create_time DESC LIMIT 1
        """, top_ids)
    else:
        c.execute(f"""
            SELECT book_id, title, page_count, create_time, user_id, click_count, is_vip_only
            FROM book {vip_filter}
            ORDER BY create_time DESC LIMIT 1
        """)
    latest_books = [dict(row) for row in c.fetchall()]
    
    # 添加封面和作者信息
    for book in top_books + latest_books:
        c.execute("SELECT image_url FROM book_page WHERE book_id=? AND page_num=1", (book["book_id"],))
        cover = c.fetchone()
        book["cover_url"] = cover["image_url"] if cover else None
        c.execute("SELECT username FROM user WHERE user_id=?", (book["user_id"],))
        user = c.fetchone()
        book["author"] = user["username"] if user else "匿名用户"
    
    return {
        "top_books": top_books,
        "latest_book": latest_books[0] if latest_books else None
    }


# ============================
# 创作者修改会员状态接口
# ============================

@app.post("/book/update-vip-status")
def update_book_vip_status(data: dict, db: sqlite3.Connection = Depends(get_db)):
    """创作者修改自己绘本的会员状态"""
    book_id = data.get("bookId")
    user_id = data.get("userId")
    is_vip_only = data.get("isVipOnly")
    
    c = db.cursor()
    c.execute("SELECT user_id FROM book WHERE book_id=?", (book_id,))
    book = c.fetchone()
    if not book:
        raise HTTPException(status_code=404, detail="绘本不存在")
    if book["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="只能修改自己的绘本")
    
    c.execute("UPDATE book SET is_vip_only=? WHERE book_id=?", (1 if is_vip_only else 0, book_id))
    db.commit()
    return {"code": 200, "msg": "修改成功"}


# ============================
# 点击量统计接口
# ============================

@app.post("/book/click/{book_id}")
def increase_click_count(book_id: str, userId: str = None, db: sqlite3.Connection = Depends(get_db)):
    """增加绘本点击量，满10次自动转为会员专享"""
    c = db.cursor()
    
    try:
        c.execute("UPDATE book SET click_count = click_count + 1 WHERE book_id=?", (book_id,))
        c.execute("SELECT user_id, click_count, is_vip_only FROM book WHERE book_id=?", (book_id,))
        book = c.fetchone()
        
        if book:
            author_id = book["user_id"]
            
            # 阅读奖励：给作者加 0.05 元
            if userId and author_id and userId != author_id:
                c.execute("UPDATE user SET total_earnings = total_earnings + 0.05 WHERE user_id=?", (author_id,))
                earning_id = str(uuid.uuid4())
                c.execute('''INSERT INTO earnings 
                    (earning_id, user_id, book_id, type, amount, source_user_id, create_time)
                    VALUES (?,?,?,?,?,?,?)''',
                    (earning_id, author_id, book_id, 'read_reward', 0.05, userId, datetime.now()))
            
            # 满10次自动转会员
            if book["click_count"] + 1 >= 10 and book["is_vip_only"] == 0:
                c.execute("UPDATE book SET is_vip_only = 1 WHERE book_id=?", (book_id,))
                db.commit()
                return {"code": 200, "msg": "成功", "converted_to_vip": True}
        
        db.commit()
        return {"code": 200, "msg": "成功", "converted_to_vip": False}
    except Exception as e:
        db.rollback()
        return {"code": 500, "msg": str(e)}


# ============================
# 绘本搜索接口
# ============================

@app.get("/books/search")
def search_books(keyword: str, userId: str = None, db: sqlite3.Connection = Depends(get_db)):
    """搜索绘本（按标题模糊匹配）"""
    c = db.cursor()
    
    is_vip = False
    if userId:
        c.execute("SELECT is_vip FROM user WHERE user_id=?", (userId,))
        user = c.fetchone()
        is_vip = user["is_vip"] if user else False
    
    search_pattern = f"%{keyword}%"
    
    if is_vip:
        c.execute("""
            SELECT book_id, title, user_id, click_count, is_vip_only, create_time
            FROM book WHERE title LIKE ?
            ORDER BY click_count DESC
        """, (search_pattern,))
    else:
        c.execute("""
            SELECT book_id, title, user_id, click_count, is_vip_only, create_time
            FROM book WHERE title LIKE ? AND is_vip_only = 0
            ORDER BY click_count DESC
        """, (search_pattern,))
    
    books = [dict(row) for row in c.fetchall()]
    
    for book in books:
        c.execute("SELECT image_url FROM book_page WHERE book_id=? AND page_num=1", (book["book_id"],))
        cover = c.fetchone()
        book["cover_url"] = cover["image_url"] if cover else None
        c.execute("SELECT username FROM user WHERE user_id=?", (book["user_id"],))
        user = c.fetchone()
        book["author"] = user["username"] if user else "匿名用户"
    
    return books


# ============================
# 用户模块
# ============================

class UserRequest(BaseModel):
    username: str
    password: str

class UserNameRequest(BaseModel):
    userId: str
    newName: str


@app.post("/user/register")
def register(data: dict, db: sqlite3.Connection = Depends(get_db)):
    phone = data.get("phone")
    username = data.get("username")
    password = data.get("password")
    
    if not phone or not username or not password:
        raise HTTPException(status_code=400, detail="手机号、昵称、密码不能为空")
    
    c = db.cursor()
    
    # 检查手机号是否已注册
    c.execute("SELECT * FROM user WHERE phone=?", (phone,))
    if c.fetchone():
        raise HTTPException(status_code=400, detail="手机号已注册")
    
    user_id = str(uuid.uuid4())
    now = datetime.now()
    c.execute("""
        INSERT INTO user (user_id, phone, username, password, is_vip, create_time, update_time, total_earnings)
        VALUES (?,?,?,?,?,?,?,?)
    """, (user_id, phone, username, password, 0, now, now, 0))
    db.commit()
    
    return {"userId": user_id, "username": username}


@app.post("/user/login")
def login(data: dict, db: sqlite3.Connection = Depends(get_db)):
    phone = data.get("phone")
    password = data.get("password")
    
    c = db.cursor()
    c.execute("SELECT * FROM user WHERE phone=? AND password=?", (phone, password))
    user = c.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    
    return {
        "userId": user["user_id"],
        "phone": user["phone"],
        "username": user["username"],
        "isVip": user["is_vip"] == 1
    }


@app.get("/user/info")
def get_user_info(userId: str, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT username, phone FROM user WHERE user_id=?", (userId,))
    user = c.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"username": user["username"], "phone": user["phone"]}


@app.post("/user/update-name")
def update_username(data: dict, db: sqlite3.Connection = Depends(get_db)):
    user_id = data.get("userId")
    new_name = data.get("newName")
    
    c = db.cursor()
    c.execute("UPDATE user SET username=?, update_time=? WHERE user_id=?", 
              (new_name, datetime.now(), user_id))
    db.commit()
    return {"code": 200, "msg": "保存成功"}


@app.post("/user/delete")
def delete_user(userId: str, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("DELETE FROM user WHERE user_id=?", (userId,))
    c.execute("DELETE FROM book WHERE user_id=?", (userId,))
    c.execute("DELETE FROM book_page WHERE book_id NOT IN (SELECT book_id FROM book)")
    c.execute("DELETE FROM vip_subscribe WHERE user_id=?", (userId,))
    c.execute("DELETE FROM system_log WHERE user_id=?", (userId,))
    db.commit()
    return {"code": 200, "msg": "账号已注销"}


@app.get("/user/books")
def get_my_books(userId: str, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT * FROM book WHERE user_id=? ORDER BY create_time DESC", (userId,))
    books = [dict(row) for row in c.fetchall()]
    
    for book in books:
        c.execute("SELECT image_url FROM book_page WHERE book_id=? AND page_num=1", (book["book_id"],))
        cover = c.fetchone()
        book["cover_url"] = cover["image_url"] if cover else None
        book["is_vip_only"] = book.get("is_vip_only", 0)
    
    return books


@app.get("/user/earnings")
def get_earnings(userId: str, db: sqlite3.Connection = Depends(get_db)):
    """获取作者收益统计"""
    c = db.cursor()
    
    c.execute("SELECT total_earnings FROM user WHERE user_id=?", (userId,))
    user = c.fetchone()
    total = user["total_earnings"] if user else 0
    
    c.execute("""
        SELECT type, amount, create_time, book_id 
        FROM earnings 
        WHERE user_id=? 
        ORDER BY create_time DESC 
        LIMIT 50
    """, (userId,))
    details = [dict(row) for row in c.fetchall()]
    
    vip_share = sum(d["amount"] for d in details if d["type"] == "vip_share")
    read_reward = sum(d["amount"] for d in details if d["type"] == "read_reward")
    
    return {
        "total": total,
        "vipShare": vip_share,
        "readReward": read_reward,
        "details": details
    }


# ============================
# 会员开通接口
# ============================

@app.post("/vip/open")
def open_vip(data: dict, db: sqlite3.Connection = Depends(get_db)):
    """开通会员，并给推荐作者分成"""
    user_id = data.get("userId")
    from_book_id = data.get("from_book_id")
    
    if not user_id:
        return {"code": 400, "msg": "用户ID不能为空"}
    
    c = db.cursor()
    
    try:
        # 检查是否已是会员
        c.execute("SELECT is_vip FROM user WHERE user_id=?", (user_id,))
        user = c.fetchone()
        if not user:
            return {"code": 404, "msg": "用户不存在"}
        if user["is_vip"] == 1:
            return {"code": 400, "msg": "已是会员"}
        
        # 开通会员
        c.execute("UPDATE user SET is_vip = 1 WHERE user_id=?", (user_id,))
        
        # 给作者分成
        if from_book_id:
            c.execute("SELECT user_id FROM book WHERE book_id=?", (from_book_id,))
            book = c.fetchone()
            if book:
                author_id = book["user_id"]
                if author_id != user_id:
                    c.execute("UPDATE user SET total_earnings = total_earnings + 1 WHERE user_id=?", (author_id,))
                    earning_id = str(uuid.uuid4())
                    c.execute('''INSERT INTO earnings 
                        (earning_id, user_id, book_id, type, amount, source_user_id, create_time)
                        VALUES (?,?,?,?,?,?,?)''',
                        (earning_id, author_id, from_book_id, 'vip_share', 1.0, user_id, datetime.now()))
        
        db.commit()
        return {"code": 200, "msg": "开通成功"}
    except Exception as e:
        print(f"开通失败: {e}")
        db.rollback()
        return {"code": 500, "msg": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)