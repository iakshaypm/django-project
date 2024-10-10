import requests

# Define the API endpoint
url = 'https://jsonplaceholder.typicode.com/users'

try:
    # Make the GET request
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()

        # Print each user's name and email
        for user in data:
            print(f"Name: {user['name']}, Email: {user['email']}")
    else:
        # If the response code is not 200, print an error message
        print(f"Failed to retrieve data. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    # Handle any errors that occur during the request
    print(f"An error occurred: {e}")
