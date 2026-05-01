import asyncio
import os
import logging
from rubpy import Client

# تنظیمات لاگ برای جلوگیری از نشت اطلاعات حساس و تمیز بودن کنسول
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logging.getLogger("rubpy").setLevel(logging.WARNING)

# محدود کردن تعداد آپلود همزمان به 3
semaphore = asyncio.Semaphore(3)

async def upload_task(app, target_guid, file_path, file_name):
    """وظیفه آپلود برای هر فایل"""
    async with semaphore:  # مدیریت صف: فقط 3 تا همزمان اجازه ورود دارند
        print(f"--- [STARTED] Uploading: {file_name}")
        try:
            # ارسال مستقیم فایل
            await app.send_document(
                object_guid=target_guid,
                document=file_path,
                caption=f"File: {file_name}"
            )
            print(f"+++ [SUCCESS] Sent: {file_name}")
        except Exception as e:
            print(f"!!! [FAILED]  {file_name}: {str(e)}")

async def main():
    # نام سشن که توسط گیت‌هاب بازیابی می‌شود
    session_name = "user_session"
    
    if not session_name:
        print("Error: RUBIKA_SESSION_NAME environment variable is not set!")
        return

    async with Client(name=session_name) as app:
        # دریافت GUID خود کاربر (Saved Messages)
        me = await app.get_me()
        target_guid = me.user.user_guid
        
        parts_dir = "downloads/parts"
        if not os.path.exists(parts_dir):
            print(f"Error: Directory {parts_dir} not found!")
            return

        # لیست کردن و مرتب‌سازی فایل‌ها
        files = sorted(os.listdir(parts_dir))
        
        if not files:
            print("No files found to upload!")
            return

        print(f"Found {len(files)} parts. Starting concurrent upload (Max 3 at a time)...")

        # ایجاد لیست وظایف (Tasks)
        tasks = []
        for file_name in files:
            file_path = os.path.abspath(os.path.join(parts_dir, file_name))
            # اضافه کردن هر آپلود به لیست تسک‌ها
            tasks.append(upload_task(app, target_guid, file_path, file_name))
        
        # اجرای تمام تسک‌ها به صورت همزمان با رعایت محدودیت Semaphore
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Main Error: {e}")
