import asyncio
import os
import logging
from rubpy import Client

# تنظیمات لاگ برای مشاهده وضعیت آپلود
logging.basicConfig(level=logging.INFO)

async def main():
    # نام سشن که توسط گیت‌هاب بازیابی می‌شود
    session_name = "user_session"
    
    async with Client(name=session_name) as app:
        me = await app.get_me()
        target_guid = me.user.user_guid
        
        parts_dir = "downloads/parts"
        # لیست کردن و مرتب‌سازی تکه‌ها برای ارسال به ترتیب درست
        files = sorted(os.listdir(parts_dir))
        
        if not files:
            print("No files found to upload!")
            return

        for file_name in files:
            file_path = os.path.abspath(os.path.join(parts_dir, file_name))
            print(f"Starting upload: {file_name}")
            

            # ارسال مستقیم با آدرس فایل (String)
            await app.send_document(
                object_guid=target_guid,
                document=file_path,  # آدرس مستقیم فایل
                caption=f"File: {file_name}"
            )
            print(f"Successfully sent: {file_name}")


if __name__ == "__main__":
    asyncio.run(main())
