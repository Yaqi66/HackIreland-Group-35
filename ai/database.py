import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def save_patient(patient_data: dict) -> dict:
    """Save patient data to Supabase"""
    response = supabase.table('patients').insert(patient_data).execute()
    return response.data[0] if response.data else None

def get_patients():
    """Get all patients"""
    response = supabase.table('patients').select('*').execute()
    return response.data

def get_patient(patient_id: str):
    """Get a specific patient"""
    response = supabase.table('patients').select('*').eq('id', patient_id).execute()
    return response.data[0] if response.data else None

def update_patient(patient_id: str, patient_data: dict) -> dict:
    """Update patient data"""
    response = supabase.table('patients').update(patient_data).eq('id', patient_id).execute()
    return response.data[0] if response.data else None

def save_image_metadata(image_data: dict) -> dict:
    """Save image metadata to Supabase"""
    response = supabase.table('images').insert(image_data).execute()
    return response.data[0] if response.data else None

def get_patient_images(patient_id: str):
    """Get all images for a patient"""
    response = supabase.table('images').select('*').eq('patient_id', patient_id).execute()
    return response.data

async def upload_image(file_path: str, patient_id: str) -> str:
    """Upload image to Supabase Storage"""
    bucket_name = "patient-images"
    file_name = f"{patient_id}/{os.path.basename(file_path)}"
    
    with open(file_path, 'rb') as f:
        response = supabase.storage.from_(bucket_name).upload(file_name, f)
    
    # Get public URL
    file_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
    return file_url

def list_bucket_files(bucket_name: str) -> list:
    """List all files in a Supabase storage bucket."""
    try:
        bucket = supabase.storage.from_(bucket_name)
        return bucket.list()
    except Exception as e:
        print(f"Failed to list bucket contents: {str(e)}")
        return []

def upload_file_to_bucket(file_data: bytes, bucket_name: str, destination_path: str, content_type: str = None) -> str:
    """
    Upload file data to a Supabase storage bucket.
    
    Args:
        file_data (bytes): The file data to upload
        bucket_name (str): Name of the Supabase storage bucket
        destination_path (str): Path within the bucket where the file should be stored
        content_type (str, optional): The content type of the file
    
    Returns:
        str: Public URL of the uploaded file
    """
    try:
        # List current files in bucket
        print("Current files in bucket:")
        
        def dump_files_to_console(files):
            for file in files:
                if file['name'] is None or file['metadata'] is None or file['metadata']['size'] is None:
                    print('Spurious file being skipped')
                    continue
                print(f"- {file['name']} (size: {file['metadata']['size']} bytes)")

        dump_files_to_console(list_bucket_files(bucket_name))
        
        # Upload file
        bucket = supabase.storage.from_(bucket_name)
        response = bucket.upload(destination_path, file_data, file_options={"contentType": content_type} if content_type else None)
        
        # Get public URL
        public_url = bucket.get_public_url(destination_path)
        
        print("\nAfter upload - files in bucket:")
        dump_files_to_console(list_bucket_files(bucket_name))
            
        return public_url
        
    except Exception as e:
        raise Exception(f"Failed to upload file to Supabase: {str(e)}")

def download_file(bucket_name: str, file_path: str) -> bytes:
    """
    Download a file from a Supabase storage bucket.
    
    Args:
        bucket_name (str): Name of the Supabase storage bucket
        file_path (str): Path to the file within the bucket
    
    Returns:
        bytes: The file data
    """
    try:
        bucket = supabase.storage.from_(bucket_name)
        response = bucket.download(file_path)
        return response
    except Exception as e:
        raise Exception(f"Failed to download file from Supabase: {str(e)}")

def delete_file(bucket_name: str, file_path: str) -> None:
    """
    Delete a file from a Supabase storage bucket.
    
    Args:
        bucket_name (str): Name of the Supabase storage bucket
        file_path (str): Path to the file within the bucket
    """
    try:
        bucket = supabase.storage.from_(bucket_name)
        bucket.remove([file_path])
    except Exception as e:
        raise Exception(f"Failed to delete file from Supabase: {str(e)}")

if __name__ == "__main__":
    print(get_patients())
    final_result = upload_file_to_bucket(
        open("p", 'rb').read(),
        "patient-images",
        "mzrr25.jpg"
    )
    print("\nUpload result URL:", final_result)
