import discord
import paramiko
import os
from discord.ext import commands
import asyncio
import smtplib
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

#엄준식
@bot.command()
async def 엄준식(ctx):
    await ctx.send("엄준식은 살아있다")

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