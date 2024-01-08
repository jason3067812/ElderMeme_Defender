from flask import Flask, request
import json

# LINE Message API 
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# gemini
import PIL.Image
import google.generativeai as genai

GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')


app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                   
    try:
        json_data = json.loads(body)                        
        line_bot_api = LineBotApi()
        handler = WebhookHandler('d2aa5af2f14e6afd395a55db6dc3b8aa')                 
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINE 收到的訊息類型
   
        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            # reply = msg
      
        elif type == 'image':
            msgID = json_data['events'][0]['message']['id']  # 取得訊息 id
            message_content = line_bot_api.get_message_content(msgID)  # 根據訊息 ID 取得訊息內容
            with open(f'C:/Users/ee527/Downloads/line_bot/image/{msgID}.png', 'wb') as fd:
                fd.write(message_content.content)
                
            img = PIL.Image.open(f'C:/Users/ee527/Downloads/line_bot/image/{msgID}.png')
            
            prompt = "如果這是一張長輩圖,祝福圖,關心圖的話請回傳1,不是的話則回傳0"

            response = model.generate_content([prompt, img], stream=True)
            response.resolve()  
            print("======================================")
            print(response.text)
            print("======================================")
            if int(response.text) == 1:
                response = model.generate_content(["根據圖上祝福或關心的話給予回覆", img], stream=True)
                response.resolve() 
                reply = response.text + "No more長輩圖謝謝"
            else:
                pass
            
 
        print(reply)
        line_bot_api.reply_message(tk,TextSendMessage(reply))  # 回傳訊息
    except:
        print(body)                                            # 如果發生錯誤，印出收到的內容
    return 'OK'                                                # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()