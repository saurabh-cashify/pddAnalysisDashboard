from pdd_db_client.client import Client

if __name__ == "__main__":
     
    client = Client()
    client.downloader.download_masks(
        imgs_mapping="/Users/saurabhsingh/Downloads/root/saurabh_utils/mapping_dents.json",
        download_path="/Users/saurabhsingh/Downloads/root/saurabh_utils/seg_dataset/dent_masks",
    )
    client.downloader.download_original_images(
        imgs_mapping="/Users/saurabhsingh/Downloads/root/saurabh_utils/mapping_dents.json",
        download_path="/Users/saurabhsingh/Downloads/root/saurabh_utils/seg_dataset/dent_images",
    )