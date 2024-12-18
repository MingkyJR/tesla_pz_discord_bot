import discord
import paramiko
import os
from discord.ext import commands
import asyncio
import smtplib
from datetime import datetime
import pytz
import random
from email.mime.text import MIMEText
from dotenv import load_dotenv


#환경변수-----------------------------------------------------------------------------------------------------
load_dotenv()
# 디스코드 봇 토큰
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
VM_HOST = os.getenv('VM_HOST')
VM_USERNAME = os.getenv('VM_USERNAME')
VM_PRIVATE_KEY_PATH = os.getenv('VM_PRIVATE_KEY_PATH')  # GCP SSH 키 파일 경로
VM_PASSWORD = os.getenv('VM_PASSWORD')

#이메일
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 이메일 발송 함수---------------------------------------------------------------------------------------
def send_email(subject, body, to_email):
    sender_email = SENDER_EMAIL  # 보내는 이메일
    sender_password = SENDER_PASSWORD  # 이메일 비밀번호 (또는 앱 비밀번호)
    smtp_server = "smtp.naver.com"  # naver SMTP 서버
    smtp_port = 465  # naver SMTP 포트

    msg = MIMEText(body)

    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    try:
        # SMTP SSL 연결
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)  # 로그인
            server.sendmail(sender_email, to_email, msg.as_string())  # 이메일 전송
            print(f"이메일이 성공적으로 전송되었습니다: {to_email}")
    except smtplib.SMTPException as e:
        print(f"SMTP 오류 발생: {str(e)}")
    except Exception as e:
        print(f"일반 오류 발생: {str(e)}")


#디스드 봇 코드-------------------------------------------------------------------------------------
#봇 준비
@bot.event
async def on_ready():
    print('Bot: {}'.format(bot.user))

#hi
@bot.command()
async def hi(ctx):
    await ctx.send("네 반갑습니다")
    
#패치노트
@bot.command()
async def 패치노트(ctx):
    await ctx.send("[좀보이드 서버 관리 봇 버전 5.1 패치노트]")
    await ctx.send('"권성빈전역까지남은시간 이 추가되었습니다. 서버접속정보 가 추가되었습니다."')

#엄준식
@bot.command()
async def 엄준식(ctx):
    # 답변 리스트
    responses = [
        "엄준식은 살아있다",
        "엄준식은 생사 불명이다"
    ]
    
    # 랜덤으로 답변 선택
    response = random.choice(responses)
    
    # 메시지 전송
    await ctx.send(response)

#류준선시간
@bot.command()
async def 류준선시간(ctx):
    # 캘리포니아 시간 가져오기
    california_tz = pytz.timezone("America/Los_Angeles")
    california_time = datetime.now(california_tz).strftime("%Y년%m월%d일 %H시%M분")
    
    # 메시지 전송
    await ctx.send(f"현재 류준선 시간은: {california_time} 입니다!")

#최진형시간
@bot.command()
async def 최진형시간(ctx):
    # 유타 주 시간 가져오기
    utah_tz = pytz.timezone("America/Denver")  # 유타 주는 MST(산악 표준시)를 사용
    now = datetime.now(utah_tz)

    # 원하는 출력 형식으로 시간 포맷 변경
    formatted_time = now.strftime("%Y년%m월%d일 %H시%M분")
    
    # 메시지 전송
    await ctx.send(f"현재 최진형 시간은 {formatted_time} 입니다")

#권성빈전역까지남은시간
@bot.command()
async def 권성빈전역까지남은시간(ctx):
    # 메시지 전송
    await ctx.send("버그가 발생했습니다(Error code 404)")
    await ctx.send("존재하지 않는 시간입니다")
    await ctx.send("권성빈은 전역할 수 없습니다")

#한국시간
@bot.command()
async def 한국시간(ctx):
    # 한국 시간 가져오기
    korea_tz = pytz.timezone("Asia/Seoul")  # 한국 표준시 (KST)
    now = datetime.now(korea_tz)

    # 원하는 출력 형식으로 시간 포맷 변경
    formatted_time = now.strftime("%Y년%m월%d일 %H시%M분")
    
    # 메시지 전송
    await ctx.send(f"현재 한국 시간은 {formatted_time} 입니다")

#서버 접속정보
@bot.command()
async def 서버접속정보(ctx):
    multi_line_string = """
    [서버 접속 정보]
    - 서버 이름 : 아무거나
    - IP : 34.84.168.168
    - LAN IP : 공백
    - 포트 : 16261 (기본)
    - 서버 암호 : 12341234
    - 서버 설명 : 맘대루
    - 유저이름 : 아무거나
    - 비밀번호 : 아무거나
    - Use Steam Relay 체크

    -> 저장 후 접속
    """
    await ctx.send(multi_line_string)

#서버재시작
@bot.command()
async def 서버재시작(ctx):
    await ctx.send("서버를 종료합니다...")
    send_email("서버 재기동 시작", "서버 재기동이 시작되었습니다.", TO_EMAIL)
    try:
        # SSH 연결 설정
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=VM_HOST,
            username=VM_USERNAME,
            password=VM_PASSWORD,
            key_filename=VM_PRIVATE_KEY_PATH,
        )


        stdin, stdout, stderr = ssh_client.exec_command("screen -S pzserver -X stuff 'quit\n'")
        stdout.channel.recv_exit_status()

        await asyncio.sleep(5)
        log_found = False
        while not log_found:
            # Logs 폴더 내 가장 최근 파일 경로 확인
                stdin, stdout, stderr = ssh_client.exec_command(
                    "ls -t /home/pzuser/Zomboid/Logs/*_DebugLog-server.txt | head -n 1"
                )
                log_file_path = stdout.read().decode().strip()

                # 파일 내용 확인
                stdin, stdout, stderr = ssh_client.exec_command(
                    f"tail -n 1 {log_file_path}"
                )
                last_line = stdout.read().decode().strip()
                if "LogOff" in last_line:
                    await ctx.send('서버가 종료되었습니다. 서버를 재시작합니다... 잠시만 기다려 주세요.....')
                    print('logOffed')
                    log_found = True
                else:
                    await asyncio.sleep(2)

        await asyncio.sleep(5)
        stdin, stdout, stderr = ssh_client.exec_command(
            "screen -S pzserver -X stuff 'bash start_server.sh\n'"
        )
        stdout.channel.recv_exit_status()

        await asyncio.sleep(30)
        log_found = False
        while not log_found:
            # Logs 폴더 내 가장 최근 파일 경로 확인
                stdin, stdout, stderr = ssh_client.exec_command(
                    "ls -t /home/pzuser/Zomboid/Logs/*_DebugLog-server.txt | head -n 1"
                )
                log_file_path = stdout.read().decode().strip()

                # 파일 내용 확인
                stdin, stdout, stderr = ssh_client.exec_command(
                    f"tail -n 1 {log_file_path}"
                )
                last_line = stdout.read().decode().strip()
                if "[MPStatistics]" in last_line:
                    print('started')
                    log_found = True
                else:
                    await asyncio.sleep(10)

        await ctx.send('서버가 정상적으로 실행되었습니다. 접속 가능합니다.')

    except Exception as e:
        await ctx.send(f"작업 중 오류가 발생했습니다: {str(e)}")
        send_email("서버 재기동 중 오류발생", f"작업 중 오류가 발생했습니다: {str(e)}", TO_EMAIL)

    finally:
         ssh_client.close()

bot.run(DISCORD_TOKEN)