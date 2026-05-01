import asyncio
import os
import logging
from rubpy import Client

logging.basicConfig(level=logging.INFO)
logging.getLogger("rubpy").setLevel(logging.WARNING)

async def upload_parts():
    # سشن از طریق متغیر محیطی که گیت‌هاب می‌سازد خوانده می‌شود
    session_data = os.getenv("hadi") 
    
    async with Client(name=session_data) as app:
        me = await app.get_me()
        target_guid = me.user.user_guid
        
        # مسیر پوشه‌ای که تکه‌های فایل در آن هستند
        folder_path = "downloads/parts"
        files = sorted(os.listdir(folder_path))

        for file_name in files:
            full_path = os.path.join(folder_path, file_name)
            logging.info(f"Sending to Rubika: {file_name}")
            
            try:
                # آپلود و ارسال
                await app.send_document(
                    object_guid=target_guid,
                    document=full_path,
                    caption=f"Part: {file_name}"
                )
                logging.info(f"Finished: {file_name}")
            except Exception as e:
                logging.error(f"Failed to upload {file_name}: {e}")

if __name__ == "__main__":
    asyncio.run(upload_parts())
