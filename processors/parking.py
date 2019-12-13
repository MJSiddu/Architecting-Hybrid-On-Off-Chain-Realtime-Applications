def process(entry_data,exit_data):
  processed_data = dict(exit_data)
  processed_data['isWanted'] = False
  processed_data['accumulated_penalty'] = 100
  processed_data['rate_per_hour'] = 10
  processed_data['tot_amount'] = 30
  return processed_data