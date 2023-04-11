# I Could use the openSkys API, to gather information on flights.
# I would be looking for military aircrafts that are not Canadian and that are within a speicifc distance from canadian air-space
# I could also look at the direction of the flight to see if it looks like it's going to come into canadian air space.
# If it is in candian air-space or trending towards candian air-space display all information
# Depending on capabilities we could also look for specific altitudes? Or speeds?
import requests

endpoint = "https://opensky-network.org/api/states/all"

response = requests.get(endpoint)

# check if the request was successful
if response.status_code == 200:
    # extract the state vectors from the JSON response
    data = response.json()
    for state in data["states"]:
        if state[2] == 'Canada':
            print(state)
else:
    print("Error:", response.status_code, response.reason)