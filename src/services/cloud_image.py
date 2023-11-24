import hashlib
from turtle import width
import cloudinary
import cloudinary.uploader
from src.conf.config import settings

class CloudImage():
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
        
    @staticmethod
    def generate_folder_name(email: str):
        """
        The generate_folder_name function takes an email address as input and returns a 12-character string.
        The returned string is the first 12 characters of the SHA256 hash of the email address.
        
        :param email: str: Specify the type of parameter that is passed to the function
        :return: A folder name for a given email address
        :doc-author: Trelent
        """
        folder_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return folder_name
    
    @staticmethod
    def upload(file, public_id: str):
        """
        The upload function takes a file and public_id as arguments.
        The function then uploads the file to Cloudinary with the given public_id, overwriting any existing files with that id.
        
        
        :param file: Specify the file to be uploaded
        :param public_id: str: Set the name of the image in cloudinary
        :return: A dict
        :doc-author: Trelent
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r
    
    @staticmethod
    def get_url_for_avatar(public_id, r):
        """
        The get_url_for_avatar function takes a public_id and an optional resource dictionary.
        It returns the URL for the avatar image, which is a 250x250px crop of the original image.
        
        :param public_id: Identify the image to be uploaded
        :param r: Get the version of the image
        :return: A url for the avatar image
        :doc-author: Trelent
        """
        src_url = cloudinary.CloudinaryImage(public_id) \
            .build_url(width=250, height=250, crop='fill', version=r.get('version'))
        return src_url
