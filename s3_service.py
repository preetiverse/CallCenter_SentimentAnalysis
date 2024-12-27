import aiohttp
import aiofiles

async def download_audio_from_url(audio_url: str):
    """Download audio file from the provided URL and save it locally."""

    # Extract the file name from the URL
    filename = audio_url.split('/')[-1].split('?')[0]
    file_path = f"uploads/{filename}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, 'wb') as f:
                        await f.write(await response.read())
                    return file_path
                else:
                    raise Exception(f"Failed to download file. HTTP Status: {response.status}")
    except Exception as e:
        raise Exception(f"Error downloading file: {str(e)}")
