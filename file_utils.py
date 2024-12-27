import aiofiles

async def save_file(file, file_path):
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file.read())
