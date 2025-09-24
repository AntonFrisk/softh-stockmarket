# softh-stockmarket
Data pipeline for getting the winners on todays stock market

⚙️ Demo of the logic:
- Run `pipe.py` for simple testing of core functions in the data handling. 

🏠 Demo of the REST API locally.
1. Run `/api/main.py` in terminal. Starts local server at `http://0.0.0.0:8000`
2. Run `demo_api.py` in another terminal to test the two api endpoints.

API endpoints:
- /get_daily_winners/ -- getting top 3 daily winners from the locally stored CSV. CSV loaded fresh for every call
- /get_daily_winners_from_file -- getting top 3 daily winners from a CSV file upload.


🌐 Demo of the REST API deployed as a Vercel function:
1. Run `demo_api.py` in the terminal. set `RUN_LOCAL = False` to avoid local setup. The
API is depolyed at `https://stockmarket-demo.vercel.app/`


Notes:
- Safe reading of CSV is used. The CSV `data1.csv` may be edited at any time
- Original template JSON in `winners_data1_template.json` has been modified, since the PDF had some wrong brackets
- 