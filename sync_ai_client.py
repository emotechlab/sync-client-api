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
            status = self.check_status(job_id, self.token)
            if status["message"] == "finished":
                break
            elif status["message"] == "failed":
                print("Job {} failed with: {}".format(job_id, status))
                return status
        resp = requests.get(os.path.join(self.url, f"download?jobId={job_id}&token={self.token}"))
        
        if resp.status_code is not 200:
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
            headers = {'Content-Type': 'application/json'}
            print(job)
            with open(audio_file, "rb") as fp:
                resp = requests.post(
                    os.path.join(self.url, f"generate?token={self.token}"), 
                    files={"audio": fp, "job": json.dumps(job, indent=2).encode('utf-8')}
                )
                print(resp.json())
        else: 
            resp = requests.post(os.path.join(self.url, f"generate?token={self.token}"), json=job)
        # except sp.CalledProcessError:
        #     resp = None

        print(resp.json())
        if not resp:
            response = {"error": "curl request failed"}
        else:
            response = resp.json()

        if display:
            print(response)

        return response

    def generate_and_download_from_file(self, save_dir, input_file):
        """ 
        input_file should be a json with sample labels/ids (eg 1, 2, 3..) and a dictionary of settings/arguments to use for that sample
        eg.
        {
            "1": {
                "language": "en-US",
                "actor": "james",
                "text": "I am powered by Emotech's revolutionary A.I. technology",
                "camera": 0,
                "background_rgb": "200,200,200",
                "emotion": "happy",
                "expression_level": 1.0

            },
            ...
        }

        - Generate method responses are saved in a json file in the save_dir 
        with the same name as the input file with '_results' appended to the end.
        - Generated content is downloaded to save_dir labelled with the sample id.

        ** NOTE **
        This function waits for each video to be generated, then downloaded before sending the next request
        """
        with open(input_file, "r") as json_file:
            input_samples = json.load(json_file)

        if "samples" not in input_samples:
            raise Exception("Input json file incorrect format, needs \"samples\" field")

        # prepare results file
        results_file = f"{os.path.splitext(input_file)[0]}_results.json"
        if not os.path.exists(results_file):
            open(results_file, 'a').close()
        
        # default arguments for required fields 
        # These will be overridden by values for each sample in the sentences file
        default_args = {
            "target_rig": "metahumans", 
            "token": self.token, 
        }
        if "default_settings" in input_samples:
            for arg, value in input_samples["default_arg_names"].items():
                if arg not in self.valid_fields:
                    raise Exception("Default arg name {} not valid, must be one of {}".format(arg, self.valid_fields))
                default_args[arg] = value
            

        results = {}
        
        # send requests
        for sample_id, args_dictionary in tqdm(input_samples["samples"].items()):
            args = default_args
            if "text" not in args_dictionary:
                raise Exception("Input sample {} is missing text field".format(sample_id))
            for key, value in args_dictionary.items():
                if key not in self.valid_fields:
                    raise Exception("Input sample {} has invalid field: {}".format(sample_id, key))
                args[key] = value

            response = self.send_request(**args)
            results[sample_id] = response

            output_type = None
            if "output_type" in args:
                output_type = args["output_type"]

            save_file = os.path.join(save_dir, sample_id + file_extension_from_output_type(output_type))
            status = self.download_content(response["jobId"], save_file)

            # if content download fails, save it to the results dictionary
            if status is not None:  
                results[sample_id] = {results[sample_id], status}
            
        with open(results_file, "w") as fp:
            json.dump(results, fp, indent=4)

