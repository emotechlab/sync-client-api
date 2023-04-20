import argparse
from video_client import SyncAiVideoClient

def main(args):
    sync_client = SyncAiVideoClient(token=args.token)

    resp = sync_client.generate(
                    args.text,
                    args.language,
                    args.target_rig,
                    actor=args.actor,
                    camera=args.camera,
                    tts_voice=args.tts_voice,
                    tts_speed=args.tts_speed,
                    background_rgb=args.background_rgb,
                    audio_url=args.audio_url,
                    audio_file=args.audio_file,
                    emotion=args.emotion,
                    emotion_level=args.emotion_level,
                    frame_width=args.frame_width,
                    frame_height=args.frame_height,
                    display=True)
    
    if "jobId" in resp:
        sync_client.download_content(resp["jobId"], args.output_file)
    else:
        print("Generate request failed: ", resp)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', type=str, required=True, help='Language of the text. See API docs for available language codes')
    parser.add_argument('--token', type=str, required=True, help='User token tied to the account - it is used to validate the user identity.')
    parser.add_argument('--text', type=str, required=True, help='Text for avatar to speak')
    parser.add_argument('--output_file', type=str, required=True, help='File to save generated content to.')
    parser.add_argument('--actor', type=str, default="caprica", choices=['caprica', 'annie', 'simone', 'vi', 'mario', 'troy', 'valerio', 'danbing', 'lewis', 'laura', 'liz', 'jeremy', 'james'], help='Actor to use in rendered video. See API documentation for more details')
    parser.add_argument('--camera', type=int, help='Camera ID', choices=[0, 1, 2, 6, 7], default=0)
    parser.add_argument('--background_rgb', type=str, help='Comma-separated RGB values for the background, eg. 120,200,120')
    parser.add_argument('--tts_voice', type=str, default=None, help="Voice of tts - consult googles TTS API documentation for options")
    parser.add_argument('--tts_speed', type=float, default=None, help="Speed of the speech, range: 0.0-1.0. 1.0 is 100% speed")
    parser.add_argument('--target_rig', type=str, default="metahumans", choices=["metahumans", "arkit"],
                        help="specifies which required rig. For the video renderer only metahumans is accepted. For FBX output we currently only accept arkit")
    parser.add_argument('--audio_url', type=str, default=None, help="Either a HTTP, S3 or OBS URL that points to an audio file to be downloaded by the engine") 
    parser.add_argument('--audio_file', type=str, default=None, help="Local path for audio file to send to the engine") 
    parser.add_argument('--emotion', type=str, default=None, choices=["neutral", "happy", "sad", "surprise", "fear", "disappointed"], help="Apply emotion expression to avatar") 
    parser.add_argument('--emotion_level', type=float, default=1.0, help="0.0 for no expression on the actor’s face, 1.0 for maximum expression.") 
    parser.add_argument('--frame_width', type=int, default=None, help='Width of frames in the generated video')
    parser.add_argument('--frame_height', type=int, default=None, help='Height of frames in the generated video')
    args = parser.parse_args()

    main(args)