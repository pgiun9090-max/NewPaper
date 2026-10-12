"""
Entry point for the Newspaper Generator.

Usage:
  # 1. 즉시 신문 제작 (어제 08:00 ~ 오늘 08:00 Gmail 수집 및 제작)
  python main.py --now

  # 2. 매일 아침 08:00 자동 스케줄러 실행
  python main.py --schedule

  # 3. 첨부 이미지(Image/img_1~3.png) 디자인과 100% 동일한 데모 신문 즉시 생성 (메일 설정 전 미리보기용)
  python main.py --demo

  # 4. Gmail IMAP 접속 및 'News' 라벨 상태 테스트
  python main.py --check-mail
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Reconfigure stdout/stderr for Unicode/Korean Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("NewsPaper")

from config import (
    GMAIL_USER,
    GMAIL_APP_PASSWORD,
    GMAIL_LABEL,
    SCHEDULE_TIME,
    OUTPUT_DIR
)
from pipeline import run_pipeline
from scheduler import start_scheduler
from mail_collector import GmailCollector, get_target_time_window

KST = timezone(timedelta(hours=9))


def check_mail_connection():
    """Checks IMAP connectivity and prints label status."""
    logger.info(f"Checking IMAP connection for user: {GMAIL_USER}")
    if not GMAIL_APP_PASSWORD:
        logger.error(
            "GMAIL_APP_PASSWORD is not set in .env!\n"
            "Please create a Google App Password at https://myaccount.google.com/apppasswords "
            "and save it in d:\\NewsPaper\\.env"
        )
        return False

    collector = GmailCollector(username=GMAIL_USER, password=GMAIL_APP_PASSWORD, label=GMAIL_LABEL)
    try:
        collector.connect()
        # 1. Recent window (including newly arrived emails up to now)
        start_recent, end_recent = get_target_time_window(use_exact_today_run=False)
        emails = collector.fetch_news_emails(start_recent, end_recent)

        # 2. Strict 8 AM to 8 AM window
        start_strict, end_strict = get_target_time_window(use_exact_today_run=True)

        print("\n" + "=" * 65)
        print("✅ Gmail IMAP 접속 및 로그인 성공!")
        print(f"📧 계정: {GMAIL_USER}")
        print(f"🏷️ 라벨: '{GMAIL_LABEL}'")
        print(f"📅 수신 범위: {start_recent.strftime('%Y-%m-%d %H:%M')} ~ {end_recent.strftime('%Y-%m-%d %H:%M')} (KST)")
        print(f"📬 대상 메일 건수: {len(emails)} 건")
        print("-" * 65)
        for i, m in enumerate(emails, 1):
            print(f"  [{i}] {m['date'].strftime('%m/%d %H:%M')} | {m['subject']} ({m['sender']})")
        print("=" * 65 + "\n")
        return True
    except Exception as e:
        logger.error(f"Gmail connection test failed: {e}")
        return False
    finally:
        collector.close()


def main():
    parser = argparse.ArgumentParser(description="나만의 신문 제작 프로그램 (Gmail + Playwright)")
    parser.add_argument("--now", action="store_true", help="지금 즉시 신문 제작 실행 (어제 08:00 ~ 오늘 08:00 메일 대상)")
    parser.add_argument("--schedule", action="store_true", help=f"매일 아침 {SCHEDULE_TIME} 자동 신문 제작 스케줄러 실행")
    parser.add_argument("--demo", action="store_true", help="첨부 이미지(Image/img_1~3.png) 디자인과 100%% 동일한 데모 신문 즉시 생성")
    parser.add_argument("--check-mail", action="store_true", help="Gmail IMAP 접속 및 'News' 라벨 메일 수신 테스트")

    args = parser.parse_args()

    # Default action if no arguments provided: run demo or guide user
    if not (args.now or args.schedule or args.demo or args.check_mail):
        print("\n" + "=" * 65)
        print("📰 나만의 신문 제작기 (Newspaper Generator)")
        print("=" * 65)
        print("사용 가능한 명령어:")
        print("  1) python main.py --demo       : 첨부 이미지와 동일한 데모 신문 생성 (미리보기)")
        print("  2) python main.py --check-mail : Gmail IMAP 연결 및 'News' 라벨 테스트")
        print("  3) python main.py --now        : 어제 08:00 ~ 오늘 08:00 메일로 지금 즉시 신문 제작")
        print("  4) python main.py --schedule   : 매일 아침 08:00 자동 신문 제작 상주 모드")
        print("=" * 65 + "\n")
        
        # If GMAIL_APP_PASSWORD is not set yet, automatically generate demo
        if not GMAIL_APP_PASSWORD:
            logger.info("GMAIL_APP_PASSWORD가 아직 비어있으므로, 첨부 이미지 기반 데모 신문을 생성합니다...")
            output_file = run_pipeline(use_demo_data=True)
            if output_file:
                print(f"🎉 데모 신문이 생성되었습니다: {output_file.resolve()}")
                print(f"   브라우저에서 열어보실 수 있습니다: file:///{output_file.resolve().as_posix()}\n")
        else:
            logger.info("지금 즉시 신문 제작을 진행합니다...")
            run_pipeline(use_demo_data=False)
        return

    if args.check_mail:
        check_mail_connection()
        return

    if args.demo:
        output_file = run_pipeline(use_demo_data=True)
        if output_file:
            print(f"\n🎉 데모 신문이 성공적으로 생성되었습니다!")
            print(f"📄 파일 경로: {output_file.resolve()}")
            print(f"🌐 브라우저 링크: file:///{output_file.resolve().as_posix()}\n")
        return

    if args.now:
        logger.info("즉시 신문 제작 파이프라인을 실행합니다...")
        output_file = run_pipeline(use_demo_data=False)
        if output_file:
            print(f"\n🎉 오늘의 신문이 성공적으로 완성되었습니다!")
            print(f"📄 파일 경로: {output_file.resolve()}")
            print(f"🌐 브라우저 링크: file:///{output_file.resolve().as_posix()}\n")
        else:
            print("\n⚠️ 신문이 생성되지 않았습니다. .env 설정과 'News' 라벨 메일을 확인해주세요.")
            print("   (테스트를 원하시면 python main.py --demo 를 실행하세요)")
        return

    if args.schedule:
        start_scheduler()


if __name__ == "__main__":
    main()
