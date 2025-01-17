from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, ImageSendMessage
import io
import numpy as np
from PIL import Image
import torch
from io import BytesIO

# ใช้ Channel Access Token และ Channel Secret ของคุณ
CHANNEL_ACCESS_TOKEN = 'PkCPtIJgy3YNVi+CxK4t6BIYQA8AFI6V4OrOWN0ASd38j8pcUd5cBRqtNhmY0OkZBu+4gLk5saKXipR5gWeF12eb7lUU4MouG+0BtFARTTemEZFZcNrF882qviWspetXQsosm5rzMoEOCZOY1uB+YAdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '13c627f011ecd11511a52a230a1eedde'

# สร้าง Flask app และ line bot API
app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# รับ Webhook จาก LINE
@app.route("/callback", methods=['POST'])
def callback():
    # Get the signature and request body
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)  # This aborts the request if verification fails
    return 'OK'

# เมื่อมีการส่งข้อความหรือภาพ
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # รับข้อมูลจากภาพ
    message_content = line_bot_api.get_message_content(event.message.id)
    img_bytes = io.BytesIO(message_content.content)
    img = Image.open(img_bytes)
    
    # ประมวลผลภาพด้วยโมเดล YOLO ที่ได้ฝึกไว้
    model = torch.hub.load('ultralytics/yolov8', 'custom', path='runs/detect/train/weights/best.pt')
    results = model(img)

    # ประมวลผลผลลัพธ์ (เช่น ข้อความ, รูปภาพ หรือข้อมูลการทำนาย)
    # นี่คือการดึงผลลัพธ์ออกมา
    labels = results.names
    pred_labels = results.xyxy[0][:, -1].tolist()

    # ส่งข้อความกลับ
    response_message = "Prediction: "
    for label in pred_labels:
        response_message += f"{labels[int(label)]}, "

    # ส่งข้อความกลับไปยังผู้ใช้
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_message)
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    # รับข้อความจากผู้ใช้และตอบกลับ
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="กรุณาส่งภาพใบเตยที่ต้องการทำนาย")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
