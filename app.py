from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Base URL for the external API
EXTERNAL_API_BASE_URL = (
    "https://feed-api.tlxbw.xyz/v3/feed/list"
    "?screen_width=1080"
    "&app_version=60105582"
    "&identity_id=ac68615b719135fd9672656231a01d2f"
    "&module=discover"
    "&os_version=34"
    "&screen_height=2191"
    "&os_type=android"
    "&channel_id=ch1_popular"
    "&base_apk_env=false"
)

@app.route('/fetch-video-data', methods=['GET'])
def fetch_video_data():
    try:
        # Get the page number from the query parameter (default is 0)
        page_num = request.args.get('page_num', default=0, type=int)

        # Build the complete external API URL with pagination
        external_api_url = f"{EXTERNAL_API_BASE_URL}&page_num={page_num}"

        # Fetch data from the external API
        response = requests.get(external_api_url)
        response.raise_for_status()  # Raise an error for bad status codes

        api_data = response.json()

        # Parse the required data fields
        extracted_data = []
        if 'data' in api_data and 'list' in api_data['data']:
            for item in api_data['data']['list']:
                if 'items' in item:
                    for video in item['items']:
                        # Extract the required fields
                        video_data = {
                            "default_url": video.get("img", {}).get("default_url"),
                            "nick_name": video.get("provider_obj", {}).get("nick_name"),
                            "title": video.get("title"),
                            "sources": [
                                {
                                    "download_url": source.get("download_url"),
                                    "filesize": source.get("filesize"),
                                    "resolution": source.get("resolution"),
                                    "url": source.get("url")
                                } for source in video.get("source_list", [])
                            ]
                        }
                        extracted_data.append(video_data)

        # Return the extracted data as JSON
        return jsonify({"videos": extracted_data}), 200

    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch data from the external API.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
