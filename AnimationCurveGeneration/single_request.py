import argparse
from animation_client import SyncAiAnimationClient

def main(args):
    sync_client = SyncAiAnimationClient(token=args.token)

    resp = sync_client.generate(
                    args.text,
                    args.language,
                    args.target_rig,
                    tts_voice=args.tts_voice,
                    tts_speed=args.tts_speed,
                    audio_url=args.audio_url,
                    audio_file=args.audio_file,
                    emotion=args.emotion,
                    emotion_level=args.emotion_level,
                    output_type=args.output_type,
                    actor=args.actor,
                    display=True)
    
    if "jobId" in resp:
        sync_client.download_content(resp["jobId"], args.output_file)
    else:
        print("Generate request failed: ", resp)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', type=str, help='Language of the text. See API docs for available language codes', required=True)
    parser.add_argument('--token', type=str, required=True, help='User token tied to the account - it is used to validate the user identity.')
    parser.add_argument('--text', type=str, help='Text for avatar to speak', required=True)
    parser.add_argument('--output_file', type=str, required=True, help='Folder to save generated content to.')
    parser.add_argument('--actor', type=str, default=None, choices=['male', 'female', 'caprica', 'annie', 'simone', 'vi', 'mario', 'troy', 'valerio', 'danbing', 'lewis', 'laura', 'liz', 'jeremy', 'james'], help="Name of the actors voice to use. This field is not required if an audio file is provided or tts voice is set.")
    parser.add_argument('--tts_voice', type=str, default=None, help="Voice of tts - consult googles TTS API documentation for options")
    parser.add_argument('--tts_speed', type=float, default=None, help="Speed of the speech, range: 0.0-1.0. 1.0 is 100% speed")
    parser.add_argument('--target_rig', type=str, default="metahumans", choices=["metahumans", "arkit"],
                        help="specifies which required rig. For the video renderer only metahumans is accepted. For FBX output we currently only accept arkit")
    parser.add_argument('--audio_url', type=str, default=None, help="Either a HTTP, S3 or OBS URL that points to an audio file to be downloaded by the engine") 
    parser.add_argument('--audio_file', type=str, default=None, help="Local path for audio file to send to the engine") 
    parser.add_argument('--emotion', type=str, default=None, choices=["neutral", "happy", "sad", "surprise", "fear", "disappointed"], help="Apply emotion expression to avatar") 
    parser.add_argument('--emotion_level', type=float, default=1.0, help="0.0 for no expression on the actor’s face, 1.0 for maximum expression.") 
    parser.add_argument('--output_type', type=str, default="csv", help='Content type to be generated', choices=["fbx", "csv"])
    args = parser.parse_args()

    main(args)