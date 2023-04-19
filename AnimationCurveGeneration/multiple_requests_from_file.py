import argparse
from sync_ai_client import SyncAiClient

def main(args):
    sync_client = SyncAiClient(token=args.token)
    sync_client.generate_and_download_from_file(args.input_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, required=True, help='User token tied to the account - it is used to validate the user identity.')
    parser.add_argument('--input_file', type=str, required=True, help='Path to json file containing inputs and job specifications')