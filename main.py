from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd

# The Flask app object must be named 'app' for Vercel to find it.
app = Flask(__name__)
CORS(app) 

@app.route('/api/trends', methods=['GET'])
def get_trends():
    # Get parameters from the request URL
    keyword = request.args.get('keyword', 'Python')
    timeframe = request.args.get('timeframe', 'today 12-m')
    geo = request.args.get('geo', 'world')
    
    if not keyword:
        return jsonify({"error": "Keyword parameter is required"}), 400

    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        
        kw_list = [keyword]
        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo, gprop='')
        
        df = pytrends.interest_over_time()

        if df.empty or keyword not in df.columns:
            return jsonify({"error": "Could not retrieve data for this keyword. It may have low search volume."}), 404

        df.reset_index(inplace=True)
        
        labels = df['date'].dt.strftime('%Y-%m-%d').tolist()
        data_points = df[keyword].tolist()
        
        return jsonify({
            "labels": labels,
            "dataPoints": data_points
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred while fetching data from Google Trends."}), 500

# NOTE: The "if __name__ == '__main__':" block is removed for Vercel deployment.
# Vercel provides its own server to run the 'app' object.

