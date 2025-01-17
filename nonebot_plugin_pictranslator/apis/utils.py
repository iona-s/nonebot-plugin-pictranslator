# from io import BytesIO
# from PIL import Image
#
# def shrink_image(image: bytes, max_size_in_mb: int) -> bytes:
#     if len(image) < max_size_in_mb * 1024 * 1024:
#         return image
#     img = Image.open(BytesIO(image))
#     buffer = BytesIO()
#     img.save(buffer, quality=50)
