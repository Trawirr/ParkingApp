import cv2
import vlc
import time
import os.path
import argparse
import threading

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", action="store_true", help="capture images", default=False)
    parser.add_argument("-v", "--video", action="store_true", help="capture videos", default=False)
    parser.add_argument("-s", "--sleep", type=int, help="time (in seconds) to sleep between capturing", default=60)
    parser.add_argument("-l", "--length", type=int, help="video length (in seconds)", default=10)
    parser.add_argument("-p", "--path", type=str, help="path to output directory", default='')
    parser.add_argument("-c", "--cameras", type=str, nargs='+', help="list of camera names", default=[])
    return parser.parse_args()

def collect_images(rtsp_url, sleep, output_dir, camera_name):
    vlc_instance = vlc.Instance('--no-xlib')
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(rtsp_url)
    player.set_media(media)
    player.play()
    time.sleep(5)

    try:
        while True:
            filename = os.path.join(output_dir, f"{camera_name}_{time.strftime('%Y_%m_%d_%H_%M')}.jpg")
            frame = player.video_take_snapshot(0, filename, 1920, 1080)
            print(f"{frame=}")
            if frame >= 0:
                print(f"Saved frame: {filename}")
                print(f"waiting {sleep}s...")
                time.sleep(sleep)
            else:
                player.stop()
                print("Reloading player...")
                time.sleep(2)
                media = vlc_instance.media_new(rtsp_url)
                player.set_media(media)
                player.play()
                
    except KeyboardInterrupt:
        player.stop()
        media.release()
        print("Exiting...")

def collect_videos(rtsp_url, sleep, length, output_dir, camera_name):
    vlc_instance = vlc.Instance('--no-xlib')
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(rtsp_url)

    try:
        while True:
            vid_len = 0
            filename = os.path.join(output_dir, f"{camera_name}_{time.strftime('%Y_%m_%d_%H_%M')}.mpg")
            media.add_option(f"sout=file/ts:{filename}")
            player = vlc_instance.media_player_new()
            player.set_media(media)
            player.play()
            time.sleep(2)
            while vid_len < length or length == 0:
                time.sleep(.5)
                #checks if the file exists and not empty
                if os.path.isfile(filename) and (os.path.getsize(filename) > 0):
                    video_file = cv2.VideoCapture(filename)
                    frames = int(video_file.get(cv2.CAP_PROP_FRAME_COUNT))
                    fps = (video_file.get(cv2.CAP_PROP_FPS))
                    vid_len = frames/fps
            player.stop()
            print(f"Saved video: {filename}")
            print(f"waiting {sleep}s...")
            time.sleep(sleep)
            
    except KeyboardInterrupt:
        player.stop()
        media.release()
        print("Exiting...")

def load_url(camera_name):
    path = fr"C:\Users\gtraw\OneDrive\Pulpit\UM sem. 2\ProjektBadawczy\apps\camera\pass\{camera_name}.txt"
    with open(path) as f:
        return f.read().strip()

def start_capture_for_camera(camera_name, args):
    url = load_url(camera_name)
    if args.image:
        collect_images(url, args.sleep, args.path, camera_name)
    elif args.video:
        collect_videos(url, args.sleep, args.length, args.path, camera_name)

if __name__ == "__main__":
    args = parse_args()
    threads = []
    
    for camera_name in args.cameras:
        thread = threading.Thread(target=start_capture_for_camera, args=(camera_name, args))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
