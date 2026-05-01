import asyncio
import os
import logging
import sys
from rubpy import Client

# تنظیمات لاگ برای جلوگیری از نشت اطلاعات حساس و تمیز بودن کنسول
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logging.getLogger("rubpy").setLevel(logging.WARNING)

# محدود کردن تعداد آپلود همزمان به 3
semaphore = asyncio.Semaphore(3)

async def upload_task(app, target_guid, file_path, file_name):
    async with semaphore:
        print(f"--- [STARTED] Uploading: {file_name}")
        try:
            await app.send_document(
                object_guid=target_guid,
                document=file_path,
                caption=f"File: {file_name}"
            )
            print(f"+++ [SUCCESS] Sent: {file_name}")
            return True # موفقیت
        except Exception as e:
            print(f"!!! [FAILED]  {file_name}: {str(e)}")
            return False # شکست

async def main():
    session_name = "user_session"
    
    # چک کردن وجود فایل سشن قبل از شروع
    if not os.path.exists(f"{session_name}.session") and not os.path.exists(f"{session_name}.rp"):
        print("Error: Session file not found! Login failed.")
        sys.exit(1)

    async with Client(name=session_name) as app:
        me = await app.get_me()
        target_guid = me.user.user_guid
        
        parts_dir = "downloads/parts"
        if not os.path.exists(parts_dir):
            print(f"Error: Directory {parts_dir} not found!")
            sys.exit(1)

        files = sorted(os.listdir(parts_dir))
        if not files:
            print("No files found to upload!")
            sys.exit(1)

        tasks = []
        for file_name in files:
            file_path = os.path.abspath(os.path.join(parts_dir, file_name))
            tasks.append(upload_task(app, target_guid, file_path, file_name))
        
        # اجرای تسک‌ها و دریافت نتایج
        results = await asyncio.gather(*tasks)

        # اگر حتی یکی از آپلودها شکست خورده باشد
        if False in results:
            print("\n!!! Some parts failed to upload. Marking workflow as FAILED.")
            sys.exit(1) # خروج با خطا برای اطلاع به گیت‌هاب
        
        print("\nAll parts uploaded successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1) # خروج در صورت خطای کلی (مثل قطع اینترنت یا سشن)
