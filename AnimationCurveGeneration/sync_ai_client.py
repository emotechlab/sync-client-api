import json
import os
from tqdm import tqdm
import requests


def parse_video_resolution(video_resolution):
    frame_width = None
    frame_height = None
    if video_resolution:
        if 'x' not in video_resolution:
            raise Exception("Video resolution is incorrect format. Should be of the form 1920x1080")
        parts = video_resolution.split('x')
        if len(parts) > 2:
            raise Exception("Video resolution is incorrect format. Should be of the form 1920x1080")
        frame_height = parts[0]
        frame_width = parts[1]
    return frame_width, frame_height

def file_extension_from_output_type(output_type):
    if output_type == "video":
        return ".mp4"
    elif output_type == "csv":
        return ".csv"
    elif output_type == "fbx":
        return ".fbx"
    return None

def get_tts_params(voice=None, speed=None):
    tts_params =  {
        "engine": "Google",
    }

    if voice:
        tts_params["voice"] = voice

    if speed != 0:
        tts_params["speed"] = speed

    return tts_params


class SyncAiClient:

    def __init__(self, token, url=None):
        if not url:
            self.url = "https://lipsync-ai.emotechlab.com/lipsync/"
        
        self.token = token

        self.valid_fields = ['language', 'actor', 'text', 'camera', 'background_rgb', 'sentences_file', 'tts_voice', 'tts_speed', 'target_rig', 'audio_url', 'audio_file', 'emotion', 'emotion_level', 'token', 'output_type', 'video_resolution', 'output_dir']

    def check_status(self, job_id):
        resp = requests.get(os.path.join(self.url, f"status?jobId={job_id}&token={self.token}"))
        return resp.json()

    def download_content(self, job_id, save_file):
        # check status in a loop until it is complete and then download the content
        while True:
            status = self.check_status(job_id)
            print(status)
            if status["status"] == "finished":
                break
            elif status["status"] == "failed":
                print("Job {} failed with: {}".format(job_id, status))
                return status
        resp = requests.get(os.path.join(self.url, f"download?jobId={job_id}&token={self.token}"))
        print(resp.status_code)
        print(resp.json())
        if resp.status_code != 200:
            print("Download failed: ", resp)
        else:
            # File is returned in bytes in the response
            with open(save_file, "wb") as fp:
                fp.write(resp.content)

        return None

    def generate(self, text, language, target_rig, actor=None, camera=None, tts_voice=None, tts_speed=None, background_rgb=None, audio_url=None, audio_file=None, emotion="", emotion_level=1, output_type="video", video_resolution=None, display=False):
        
        if audio_url and audio_file:
            raise Exception("Only one of audio_file or audio_url should be supplied.")

        # set emotion and level
        emotion_obj = None
        if emotion:
            emotion_obj = {
                "level": emotion_level,
                "expression": emotion
            }
        
        # set background color
        background_color = None
        if background_rgb:
            red, green, blue = background_rgb.split(",")
            background_color = {
                "red": int(red),
                "green": int(green),
                "blue": int(blue),
            }

        output = {"type": output_type}
        if output_type == "video":
            frame_width, frame_height = parse_video_resolution(video_resolution)
            output["width"] = frame_width
            output["height"] = frame_height
            output["background_color"] = background_color

        # try:
        job = {
            "target_rig": target_rig,
            "text": text,
            "language": language,
            "tts_params": get_tts_params(tts_voice, tts_speed),
            "output": output,
            "wait_time": None,
        }

        if actor:
            job["actor"] = actor

        if camera is not None:
            job["camera"] = camera

        if emotion_obj:
            job["emotion"] = emotion_obj
        
        if audio_url and audio_file:
            raise Exception("Both audio_url and audio_path are given. Only one can be used.")
        elif audio_url:
            job["audio_url"] = audio_url

        print(job)
        if audio_file:
            with open(audio_file, "rb") as fp:
                resp = requests.post(
                    os.path.join(self.url, f"generate?token={self.token}"), 
                    files={"audio": fp, "job": json.dumps(job, indent=2).encode('utf-8')}
                )
        else: 
            resp = requests.post(os.path.join(self.url, f"generate?token={self.token}"), json=job)
    
        if not resp:
            response = {"error": "curl request failed"}
        else:
            response = resp.json()

        if display:
            print(response)

        return response

    def generate_and_download_from_file(self, input_file):
        """ 
        input_file should be a json with a "jobs" field containing a list of settings/arguments to use for each sample
        Each sample must have a "language", "text", and "output_file" fields. If "output_type" is "video" (which is default),
        then the "camera" and "actor" field must be supplied as well.
        eg.
        {
            "jobs": [
                {
                    "language": "en-US",
                    "text": "I am powered by Emotech's revolutionary A.I. technology",
                    "camera": 0,
                    "actor": "caprica",
                    "output_file": "/path/to/my_video.mp4"
                },
                {
                    "language": "ar",
                    "actor": "laura",
                    "text": "أنا مدعوم بتقنية الذكاء الاصطناعي الثورية من Emotech",
                    "camera": 7,
                    "background_rgb": "150,120,180",
                    "emotion": "sad",
                    "emotion_level": 0.5,
                    "output_file": "/path/to/my_video2.mp4"
                },
                ...
            ]
        }

        - Generate method responses are saved in a json file in the save_dir 
        with the same name as the input file with '_results' appended to the end.

        ** NOTE **
        This function waits for each video to be generated, then downloaded before sending the next request
        """
        with open(input_file, "r") as json_file:
            input_samples = json.load(json_file)

        if "jobs" not in input_samples:
            raise Exception("Input json file incorrect format, needs \"jobs\" field")

        # prepare results file
        results_file = f"{os.path.splitext(input_file)[0]}_results.json"
        if not os.path.exists(results_file):
            open(results_file, 'a').close()
    
        results = {}    
        required_fields = ["text", "language", "output_file"]
        # send requests
        for sample_id, args_dictionary in tqdm(input_samples["samples"].items()):
            for field in required_fields:
                if field not in args_dictionary:
                    raise Exception("Input sample {} is missing {} field".format(sample_id, field))
            
            for key, _ in args_dictionary.items():
                if key not in self.valid_fields:
                    raise Exception("Input sample {} has invalid field: {}".format(sample_id, key))

            response = self.send_request(args_dictionary)
            results[sample_id] = response

            save_file = os.path.join(args_dictionary["output_file"])
            status = self.download_content(response["jobId"], save_file)

            # if content download fails, save it to the results dictionary
            if status is not None:  
                results[sample_id] = {results[sample_id], status}
            
        with open(results_file, "w") as fp:
            json.dump(results, fp, indent=4)

