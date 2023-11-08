from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

import os
import smtplib
import uuid

from datetime import datetime

load_dotenv()
app = FastAPI()

db = AsyncIOMotorClient(os.getenv('DB_URI'))['database']


class Notification(BaseModel):
    user_id: str
    key: str
    target_id: str = None
    data: dict = None


@app.post("/create")
async def create_notification(notification: Notification):
    user = await db['users'].find_one({'_id': notification.user_id})
    if not user:
        # Создание нового пользователя, если он не существует
        user = {'_id': notification.user_id, 'email': os.getenv('EMAIL'), 'notifications': []}
        await db['users'].insert_one(user)

    # Создание уведомления
    new_notification = notification.dict()
    new_notification_id = str(uuid.uuid4())
    new_notification['notification_id'] = new_notification_id
    new_notification['is_new'] = True
    new_notification['timestamp'] = datetime.now().timestamp()

    # Ограничение количества уведомлений
    if len(user['notifications']) >= 10:
        user['notifications'].pop(0)

    user['notifications'].append(new_notification)
    await db['users'].update_one({'_id': user['_id']}, {'$set': {'notifications': user['notifications']}})

    # Отправка электронной почты
    if notification.key in ['registration', 'new_login']:
        send_email(user['email'], new_notification)
    elif notification.key in ['new_message', 'new_post']:
        # Создание записи в документе пользователя
        if 'records' not in user:
            user['records'] = []
        new_record = {
            'notification_id': user['_id'],
            'target_id': notification.target_id,
            'data': notification.data
        }
        user['records'].append(new_record)
        await db['users'].update_one({'_id': user['_id']}, {'$set': {'records': user['records']}})

    return {"success": True}


@app.get("/list")
async def list_notifications(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    skip = data.get("skip", 0)
    limit = data.get("limit", 10)

    user = await db['users'].find_one({'_id': user_id})
    if not user:
        return {"success": False, "error": "User not found"}

    notifications = user['notifications'][skip:skip + limit]
    return {"success": True, "data": notifications}


@app.post("/read")
async def mark_notification_as_read(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    notification_id = data.get("notification_id")
    user = await db['users'].find_one({'_id': user_id})
    if not user:
        return {"success": False, "error": "User not found"}

    notification = notification = next(
        (n for n in user['notifications'] if n.get("notification_id") == notification_id), None)
    if not notification:
        return {"success": False, "error": "Notification not found"}

    notification['is_new'] = False
    await db['users'].update_one({'_id': user['_id']}, {'$set': {'notifications': user['notifications'][:-1]}})

    return {"success": True}


def send_email(to_email, notification):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SMTP_EMAIL')
    msg['To'] = to_email
    msg['Subject'] = "New notification"
    body = f"You have a new notification: {notification}"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(os.getenv('SMTP_HOST'), os.getenv('SMTP_PORT'))
    server.starttls()
    server.login(os.getenv('SMTP_LOGIN'), os.getenv('SMTP_PASSWORD'))
    text = msg.as_string()
    server.sendmail(os.getenv('SMTP_EMAIL'), to_email, text)
    server.quit()


if __name__ == '__app__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
