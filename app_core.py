#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 載入需要的模組
from __future__ import unicode_literals
from linebot.models import *
import configparser
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import requests
from bs4 import BeautifulSoup
import json
import random
import psycopg2

#查詢 Yahoo 字典
def explain(word):
    web = "https://tw.dictionary.search.yahoo.com/search?p=%s"%word
    nl_response = requests.get(web)
    soup = BeautifulSoup(nl_response.text, "html.parser")
    content = soup.findAll("div",{"class" : "fz-16 fl-l dictionaryExplanation"})
    explainationList = []
    for a in content:
        tem = a.getText()
        explainationList.append(tem)
    return explainationList
def sentence(word):
    web = "https://tw.dictionary.search.yahoo.com/search?p=%s"%word
    nl_response = requests.get(web)
    soup = BeautifulSoup(nl_response.text, "html.parser")
    content2 = soup.findAll("span",{"class" : "d-b fz-14 fc-2nd lh-20"})
    sentenceList = []
    for a in content2:
        tem2 = a.getText()
        sentenceList.append(tem2)
    return sentenceList

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 當 Line Bot 接收到文字訊息時
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id
    result_text = ""
    #Evan's user_id: U8f118085e8ec52badecac9edbe8e9bc9
    result_text += f'Hello User\n'
    
    #Connect DATABASE
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = conn.cursor()
    
    #load my_status as [ans, exam, level, exp, hp,...etc]
    postgres_select_query = f"""SELECT * FROM ans_table WHERE user_id = '{user_id}';"""
    cursor.execute(postgres_select_query)
    my_status = cursor.fetchall()[0]
    ans = my_status[2]
    exam = my_status[3]
    level = my_status[4]
    exp = my_status[5]
    hp = my_status[6]
    exam_flag = my_status[7]
    coin = my_status[8]
    ans_flag = my_status[9]
    my_vocab = my_status[10]
    my_vocab_list = my_vocab.split()
    review_flag = my_status[11]
    review_mode = my_status[12]
    review_mode_flag = my_status[13]
    review_num = my_status[14]
    review_num_flag = my_status[15]
    my_pass_vocab = my_status[16]
    my_pass_vocab_list = my_pass_vocab.split()
    my_failure_vocab = my_status[17]
    my_failure_vocab_list = my_failure_vocab.split()
    review_ans = my_status[18]
    
    # load vocabulary list
    tofelfr = open("托福五千單.txt","r")
    GREfr = open("GRE1300單.txt","r")
    toeicfr = open("多益3000單.txt","r")
    tofelList = json.load(tofelfr)
    GREList = json.load(GREfr)
    toeicList = json.load(toeicfr)
    
    try:
        #Help command
        if msg in ['!h', '!H']:
            result_text += f'任意輸入有效單字即可餵食你的專屬寵物獸\n'
            result_text += f'[支援指令集]\n'
            result_text += f'查看狀態: !s\n'
            result_text += f'考題作答: !\n'
            result_text += f'輸入答案: a, b, bd...\n'
            result_text += f'更換考題: !c\n'
            result_text += f'查詢單字解釋: &word\n'
            result_text += f'查詢已餵食單字: !w\n'
            result_text += f'刪除已餵食單字: !d word\n'
            result_text += f'複習餵食單字: !r\n'
        
        #Revise quiz source if exam_flag is True
        elif exam_flag:
            if msg == '0':
                postgres_update_query = f"""UPDATE ans_table SET exam_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
                result_text += f'維持考題 {exam} !\n'
            elif msg == '1':
                postgres_update_query = f"""UPDATE ans_table SET exam = 'GRE', exam_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit() 
                postgres_select_query = f"""SELECT exam FROM ans_table WHERE user_id = '{user_id}';"""
                cursor.execute(postgres_select_query)
                exam = cursor.fetchall()[0][0]
                result_text += f'成功將考題更換成 {exam} !\n'
            elif msg == '2':
                postgres_update_query = f"""UPDATE ans_table SET exam = '學測', exam_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
                postgres_select_query = f"""SELECT exam FROM ans_table WHERE user_id = '{user_id}';"""
                cursor.execute(postgres_select_query)
                exam = cursor.fetchall()[0][0]
                result_text += f'成功將考題更換成 {exam} !\n'
            elif msg == '3':
                postgres_update_query = f"""UPDATE ans_table SET exam = '指考', exam_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
                postgres_select_query = f"""SELECT exam FROM ans_table WHERE user_id = '{user_id}';"""
                cursor.execute(postgres_select_query)
                exam = cursor.fetchall()[0][0]
                result_text += f'成功將考題更換成 {exam} !\n'
            else:
                postgres_update_query = f"""UPDATE ans_table SET exam_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()                
                result_text += f'你輸入錯誤指令囉~\n'
        
        #Set review mode
        elif review_mode_flag:
            if msg.upper() == 'A':
                if len(my_failure_vocab_list) > 0:
                    postgres_update_query = f"""UPDATE ans_table SET review_mode = 'a', review_mode_flag = '0' \
                                            WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
                    result_text += f'曾經答錯{len(my_failure_vocab_list)}個單字，這次要複習幾個呢?\n'
                else:
                    result_text += f'恭喜你! 目前沒有答錯的單字!\n'
                    postgres_update_query = f"""UPDATE ans_table SET review_flag = '0', review_mode_flag = '0', \
                                            review_num_flag = '0' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()                    
            elif msg.upper() == 'B':
                postgres_update_query = f"""UPDATE ans_table SET review_mode = 'b', review_mode_flag = '0' \
                                        WHERE user_id = '{user_id}';"""
                cursor.execute(postgres_update_query)
                conn.commit()    
                result_text += f'目前有{len(my_vocab_list)}個單字可以複習，這次要複習幾個呢?\n'
            elif msg.upper() == 'C':
                if len(my_pass_vocab_list) > 0:
                    postgres_update_query = f"""UPDATE ans_table SET review_mode = 'c', review_mode_flag = '0' \
                                            WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()    
                    result_text += f'曾經答對{len(my_pass_vocab_list)}個單字，這次要複習幾個呢?\n'
                else:
                    result_text += f'恭喜你! 目前沒有答對的單字!\n'
                    postgres_update_query = f"""UPDATE ans_table SET review_flag = '0', review_mode_flag = '0', \
                                            review_num_flag = '0' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
            elif msg.upper() == 'ESC':
                postgres_update_query = f"""UPDATE ans_table SET review_flag = '0', review_mode_flag = '0',\
                                        review_num_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()                
                result_text += f'離開單字複習模式'
            else:
                result_text += f'請選擇單字複習模式 A, B, C 或是 ESC 離開單字複習模式'
                
        #Set review words number        
        elif review_num_flag:
            if msg.isdecimal():
                n = int(msg)
                if n > 0:
                    if review_mode == 'a':
                        if n > len(my_failure_vocab_list):
                            n = len(my_failure_vocab_list)
                        word = random.choice(my_failure_vocab_list)
                    elif review_mode == 'b':
                        if n > len(my_vocab_list):
                            n = len(my_vocab_list)
                        word = random.choice(my_vocab_list)
                    elif review_mode == 'c':
                        if n > len(my_pass_vocab_list):
                            n = len(my_pass_vocab_list)            
                        word = random.choice(my_pass_vocab_list)
                    quiz = explain(word)
                    options = [word]
                    temp = my_vocab_list
                    temp.remove(word)
                    options += random.sample(temp, 3)
                    random.shuffle(options)
                    result_text += f'[題目]:{quiz}\n對應的英文單字是下列哪一項呢?\n'
                    result_text += f'[選項]: (A){options[0]} (B){options[1]} (C){options[2]} (D){options[3]}\n'                
                    ans = options.index(word)
                    if ans == 0:
                        ans = 'A'
                    elif ans == 1:
                        ans = 'B'
                    elif ans == 2:
                        ans = 'C'
                    elif ans == 3:
                        ans = 'D'
                    ans += f'{word}'
                    postgres_update_query = f"""UPDATE ans_table SET review_ans = '{ans}', review_num = '{n-1}', \
                                            review_num_flag = '0' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()  
                else:
                    result_text += f'請輸入大於 0 的整數或是 ESC 回到上一步'
            elif msg.upper() == 'ESC':
                postgres_update_query = f"""UPDATE ans_table SET review_mode_flag = '1' WHERE user_id = '{user_id}';"""
                cursor.execute(postgres_update_query)
                conn.commit()
                result_text += f'請問你要複習單字的模式是?\n'
                result_text += f'A :再接再厲(從曾經答錯的單字中挑選)\n'
                result_text += f'B :嶄新開始(從全部學習過的單字中挑選)\n'
                result_text += f'C :精益求精(除去曾經答對的單字，從答錯或未答過的單字中挑選)\n'
                result_text += f'或輸入 ESC 離開單字複習模式\n'                
            else:
                result_text += f'請輸入大於 0 的整數或是 ESC 回到上一步'
                
        elif review_flag:
            if msg.upper() == review_ans.upper()[0]:
                result_text += f'答對了!\n剩下{review_num}個單字複習\n'
                word = review_ans[1:]
                if word not in my_pass_vocab_list:
                    my_pass_vocab_list.append(word)
                    my_pass_vocab =' '.join(my_pass_vocab_list) 
                    postgres_update_query = f"""UPDATE ans_table SET my_pass_vocab = '{my_pass_vocab}' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
                if word in my_failure_vocab_list:
                    my_failure_vocab_list.remove(word)
                    my_failure_vocab =' '.join(my_failure_vocab_list) 
                    postgres_update_query = f"""UPDATE ans_table SET my_failure_vocab = '{my_failure_vocab}' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
            else:
                result_text += f'答錯囉，正確答案是({ans})!\n剩下{review_num}個單字複習\n'
                word = review_ans[1:]
                if word not in my_failure_vocab_list:
                    my_failure_vocab_list.append(word)
                    my_failure_vocab = ' '.join(my_failure_vocab_list)
                    postgres_update_query = f"""UPDATE ans_table SET my_failure_vocab = '{my_failure_vocab}' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
                if word in my_pass_vocab_list:
                    my_pass_vocab_list.remove(word)
                    my_pass_vocab =' '.join(my_pass_vocab_list) 
                    postgres_update_query = f"""UPDATE ans_table SET my_pass_vocab = '{my_pass_vocab}' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
            if review_num > 0:
                postgres_update_query = f"""UPDATE ans_table SET review_num = '{review_num-1}',\
                                        review_num_flag = '0' WHERE user_id = '{user_id}';"""
                cursor.execute(postgres_update_query)
                conn.commit()
                if review_mode == 'a':
                    word = random.choice(my_failure_vocab_list)
                elif review_mode == 'b':
                    word = random.choice(my_vocab_list)
                elif review_mode == 'c':
                    word = random.choice(my_pass_vocab_list)
                quiz = explain(word)
                options = [word]
                temp = my_vocab_list
                temp.remove(word)
                options += random.sample(temp, 3)
                random.shuffle(options)
                result_text += f'[題目]:{quiz}\n對應的英文單字是下列哪一項呢?\n'
                result_text += f'[選項]: (A){options[0]} (B){options[1]} (C){options[2]} (D){options[3]}\n'                
                ans = options.index(word)
                if ans == 0:
                    ans = 'A'
                elif ans == 1:
                    ans = 'B'
                elif ans == 2:
                    ans = 'C'
                elif ans == 3:
                    ans = 'D'
                ans += f'{word}'
                postgres_update_query = f"""UPDATE ans_table SET review_ans = '{ans}' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()  
                
            else:
                postgres_update_query = f"""UPDATE ans_table SET review_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
            if msg.upper() == 'ESC':
                postgres_update_query = f"""UPDATE ans_table SET review_flag = '0', review_mode_flag = '0',\
                                        review_num_flag = '0' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
        #Revise quiz source
        elif msg in ['!c', '!C']:
            postgres_update_query = f"""UPDATE ans_table SET exam_flag = '1' WHERE user_id = '{user_id}';"""    
            cursor.execute(postgres_update_query)
            conn.commit()
            result_text += f'輸入 0 以放棄替換考題!\n'
            result_text += f'輸入 1 以替換考題成 GRE!\n'
            result_text += f'輸入 2 以替換考題成 學測!\n'
            result_text += f'輸入 3 以替換考題成 指考!\n'
            
        #Reviw words
        elif msg in ['!r', '!r']:
            
            if len(my_vocab_list) > 4:
                postgres_update_query = f"""UPDATE ans_table SET review_flag = '1', review_mode_flag = '1', \
                                        review_num_flag = '1' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
                result_text += f'請問你要複習單字的模式是?\n'
                result_text += f'A :再接再厲(從曾經答錯的單字中挑選)\n'
                result_text += f'B :嶄新開始(從全部學習過的單字中挑選)\n'
                result_text += f'C :精益求精(除去曾經答對的單字，從答錯或未答過的單字中挑選)\n'
                result_text += f'或輸入 ESC 離開單字複習模式\n'
            else:
                result_text += f'請先餵食寵物獸 4 個以上的單字才能開始複習單字!\n'
         
        #Check user's status
        elif msg in ['!s', '!S']:
            result_text += f'[等級]: {level}\n'
            result_text += f'[經驗值]: {exp}\n'
            result_text += f'[體力]: {hp}\n'
            result_text += f'[預設考題]: {exam}\n'
            result_text += f'[單字餵食數量]: {len(my_vocab_list)}\n'
        
        #List all words stored in my_vocab
        elif msg in ['!w', '!W']:
            result_text += f'目前已餵食寵物獸 {len(my_vocab_list)} 個單字如下:\n'
            for vocab in my_vocab_list:
                result_text += f'{vocab}\n'
            result_text += f'答對(Debud) {len(my_pass_vocab_list)} 個單字如下:\n'
            for vocab in my_pass_vocab_list:
                result_text += f'{vocab}\n'
            result_text += f'答錯(Debud) {len(my_failure_vocab_list)} 個單字如下:\n'  
            for vocab in my_failure_vocab_list:
                result_text += f'{vocab}\n'            
        #Delete the word in my_vocab        
        elif msg[:2] in ['!d', '!D']:
            word = msg[3:]
            if word not in my_vocab_list:
                result_text += f'目前已餵食的單字並沒有 {word} 這個單字喔!\n'
            else:
                my_vocab_list.remove(word)
                my_vocab = ' '.join(my_vocab_list)
                postgres_update_query = f"""UPDATE ans_table SET my_vocab = '{my_vocab}' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
                result_text += f'從已餵食的單字中刪除 {word} 這個單字!\n'
        
        #Pick a random quiz
        elif msg == '!':
            with open(f'{exam}.txt', 'r') as f:
                if exam in ['學測', '指考']:
                    result = json.load(f)
                    total_num = len(result)
                    random_num = random.randint(0, total_num-1)
                    ans = result[random_num][3][1]
                    options = result[random_num][2]
                    question = result[random_num][1]
                    result_text += f'[題目]: {question}\n'
                    result_text += f'[選項]: {options}\n'
                    result_text += f'開始作答:\n'
                    #update ans in database
                    postgres_update_query = f"""UPDATE ans_table SET ans = '{ans}' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
                    postgres_update_query = f"""UPDATE ans_table SET ans_flag = '1' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()                    
                elif exam in ['GRE']:
                    result = json.load(f)
                    total_num = len(result)
                    random_num = random.randint(0, total_num-1)
                    ans_list = result[random_num][2]
                    options_list = result[random_num][1]
                    question = result[random_num][0][0]
                    result_text += f'[題目]: {question}\n'
                    result_text += f'[選項]: '
                    for i in range(len(options_list)):
                        result_text += f'({chr(65 + i)}) {options_list[i]} '
                    result_text += f'\n'
                    result_text += f'本題需選擇 {len(ans_list)} 個答案，開始作答:\n'
                    ans = ''
                    for i in range(len(ans_list)):
                        index = options_list.index(ans_list[i])
                        ans += chr(65 + index)
                    #update ans in database
                    postgres_update_query = f"""UPDATE ans_table SET ans = '{ans}' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()                  
                    postgres_update_query = f"""UPDATE ans_table SET ans_flag = '1' WHERE user_id = '{user_id}';"""    
                    cursor.execute(postgres_update_query)
                    conn.commit()
                    
        #Enter correct anwser
        elif (msg.upper() == ans.upper()) and ans_flag:
            result_text += f'答對了!'   
            exp += 1
            if exp < 100:
                postgres_update_query = f"""UPDATE ans_table SET exp = '{exp}' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
            else:
                level += 1
                exp = exp % 100
                postgres_update_query = f"""UPDATE ans_table SET exp = '{exp}' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
                    
                postgres_update_query = f"""UPDATE ans_table SET level = '{level}' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
                         
            postgres_update_query = f"""UPDATE ans_table SET ans_flag = '0' WHERE user_id = '{user_id}';"""    
            cursor.execute(postgres_update_query)
            conn.commit()                 
        
        #Enter wrong anwser
        elif (msg.upper() != ans.upper()) and ans_flag:
            result_text += f'答錯囉，正確答案是({ans})!'
            postgres_update_query = f"""UPDATE ans_table SET ans_flag = '0' WHERE user_id = '{user_id}';"""    
            cursor.execute(postgres_update_query)
            conn.commit() 
        
        #Search the word from Yahoo dictionary
        elif msg[0] == '&':
            word = msg[1:].strip()
            explainationList = explain(word)
            sentenceList = sentence(word)
            if len(explainationList) > 0:
                result_text += f'{word} 的中文意思是:\n'
                for explaination in explainationList:
                    result_text += explaination
                    result_text += '; '
                result_text += '\n'      
                if len(sentenceList) > 0:
                    result_text += f'{word} 的例句有:\n'
                    for senten in sentenceList:
                        result_text += senten
                        result_text += '\n'     
            else:
                result_text += f'找不到這個單字唷!\n'
                
        #Add a new word into my_vocab        
        elif (len(explain(msg)) > 0) and (len(msg) > 1):
            word = msg.lower().strip()
            if word in my_vocab_list:
                result_text += f'這個字你已經學過囉!\n'    
            else:
                explainationList = explain(word)
                sentenceList = sentence(word)
                if word in GREList:
                    result_text += f'恭喜你學到 GRE 的單字 {word} !\n'
                elif word in tofelList:
                    result_text += f'恭喜你學到 Tofel 單字 {word} !\n'
                elif word in toeicList:
                    result_text += f'恭喜你學到 Toeic 單字 {word} !\n'
                else:
                    result_text += f'{word} 不是常見的英檢單字，不過 '
                result_text += f'{word} 的中文意思是:\n'
                for explaination in explainationList:
                    result_text += explaination
                    result_text += '; '
                result_text += '\n'      
                if len(sentenceList) > 0:
                    result_text += f'{word} 的例句有:\n'
                    for senten in sentenceList:
                        result_text += senten
                        result_text += '\n'  
                my_vocab_list.append(word)
                my_vocab = ' '.join(my_vocab_list)
                postgres_update_query = f"""UPDATE ans_table SET my_vocab = '{my_vocab}' WHERE user_id = '{user_id}';"""    
                cursor.execute(postgres_update_query)
                conn.commit()
        else:
            result_text += '錯誤指令，請輸入 !h 以了解更多指令!'
            
        cursor.close()
        conn.close()
    
    #Record exception condition
    except Exception as e:
        result_text = str(e)
    
    #Reply message
    finally:
        result_msg = TextSendMessage(text=result_text)
        line_bot_api.reply_message(event.reply_token, result_msg)       
        
    tofelfr.close()
    GREfr.close()
    toeicfr.close()
    
# 當 Line Bot 被追蹤時
@handler.add(FollowEvent)    
def handle_follow(event):
    
    user_id = event.source.user_id
    result_text = ""
    result_text += f'請輸入 !h 了解相關指令。\n'
    
    try:
        #Connect DATABASE
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
        cursor = conn.cursor()
    
        #Insert user_id and set default values in postgres
        table_columns = '(user_id, ans, exam, level, exp, hp, exam_flag, coin, ans_flag, my_vocab, review_flag, review_mode, review_mode_flag, review_num, review_num_flag, my_pass_vocab, my_failure_vocab, review_ans)' #All columns in postgres
        postgres_insert_query = f"""INSERT INTO ans_table {table_columns} VALUES\
                                ('{user_id}', 'A', '學測', '1', '0', '0', '0', '0', '0', '', '0', 'b', '0', '0', '0', '', '', '');"""    
        cursor.execute(postgres_insert_query)
        conn.commit()  
    finally:
        result_msg = TextSendMessage(text=result_text)
        line_bot_api.reply_message(event.reply_token, result_msg)   
    
# 當 Line Bot 被取消追蹤時 
@handler.add(UnfollowEvent)    
def handle_unfollow(event):
    
    user_id = event.source.user_id
    
    #Connect DATABASE
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')
    cursor = conn.cursor()    
    
    #Delete user_id in postgres
    postgres_delete_query = f"""DELETE FROM ans_table WHERE user_id = '{user_id}';"""    
    cursor.execute(postgres_delete_query)
    conn.commit()    
    
    
if __name__ == "__main__":
    app.run()

