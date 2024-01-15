import re
from tabulate import tabulate

import pandas as pd


def parse_log_file(log_file_path):
    logs = []
    with open(log_file_path, 'r') as file:
        for line in file:
            match = match = re.match(r".*Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Method: (\w+) - Endpoint: (\w+) - Duration \(s\) (\d+\.\d+) - Data Length: (\d+) - Horizon: (\d+) - Model: (\w+) -> (\w+)", line)
            if match:
                timestamp, method, endpoint, time_taken, data_length, horizon, request_model, response_model = match.groups()
                response_model = response_model if response_model else 'Not provided'
                logs.append({
                    'timestamp': timestamp,
                    'method': method,
                    'endpoint': endpoint,
                    'time_taken': float(time_taken),
                    'data_length': int(data_length),
                    'horizon': int(horizon),
                    'request_model': request_model,
                    'response_model': response_model,
                })
    return logs

if __name__ == "__main__":
    log_file_path = "./logs/access.log"  # Replace with your actual log file path
    logs = parse_log_file(log_file_path)
    if logs:
        df_logs = pd.DataFrame(logs)
        df_logs.to_csv('logs.csv', index=False)
        table = tabulate(logs, headers='keys', tablefmt='pretty')
        print(table)
    else:
        print("No relevant logs found.")
