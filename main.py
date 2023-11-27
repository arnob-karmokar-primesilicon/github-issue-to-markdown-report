import os, sys
import json
import requests
import pytz
from datetime import datetime, timedelta
from dotenv import load_dotenv
from issue import Issue

load_dotenv()

REPO_OWNER = sys.argv[1] # Github Repository Owner's Username
REPOSITORY = sys.argv[2] # Repository Name
GITHUB_PERSONAL_ACCESS_TOKEN = sys.argv[4]

# Define a custom sorting key function
def custom_sort_key(issue):
    # Define the order of project statuses
    status_order = {"Open": 1, "Reopened": 2, "In Progress": 3, "Need Review": 4, "Review In Progress": 5,"Done": 6}
    
    # Return a tuple for sorting, with project_status being the key
    return (status_order.get(issue.project_status, 5), issue.complete_date,issue.deadline)


# Define your GraphQL query
query = """
{
  repository(owner: "%REPO-OWNER%", name: "%REPOSITORY%") {
    issues(last: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      edges {
        node {
          title
          url
          closed
          createdAt
          closedAt
          projectItems(first: 1) {
            totalCount
            edges {
              node {
                project {
                  title
                }
                updatedAt
                id
                fieldValues(first: 20) {
                  nodes {
                    ... on ProjectV2ItemFieldSingleSelectValue {
                      field {
                        ... on ProjectV2SingleSelectField {
                          name
                        }
                      }
                      name
                    }
                    ... on ProjectV2ItemFieldDateValue {
                      field {
                        ... on ProjectV2Field {
                          name
                        }
                      }
                      date
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
query = query.replace("%REPO-OWNER%",REPO_OWNER).replace("%REPOSITORY%",REPOSITORY)
# Define your GitHub API endpoint
endpoint = 'https://api.github.com/graphql'  # Replace with your GraphQL endpoint

# Define your GitHub Personal Access Token
token = GITHUB_PERSONAL_ACCESS_TOKEN

# Set up the headers with your token
headers = {
    'Authorization': f'Bearer {token}',
}

# Make the GraphQL request
response = requests.post(endpoint, json={'query': query}, headers=headers)

# Check the response
if response.status_code == 200:
    data = response.json()
    # print(data)

    # Extract issue items
    issues = data["data"]["repository"]["issues"]["edges"]

    # Define a list to store the extracted issues as instances of the Issue class
    issue_list = []
    # Iterate through the issues and extract the required fields
    for issue in issues:
        node = issue["node"]
        issue_title = node["title"]
        issue_url = node["url"]
        is_closed = node["closed"]
        created_at = node["createdAt"]
        closed_at = node["closedAt"]

        deadline = None
        start_date = None
        complete_date = None
        project_status = None

        project_items = node["projectItems"]["edges"]
        if project_items:
            if project_items[0]["node"]["project"]:
                project = project_items[0]["node"]["project"]
            if project["title"]:
                project_title = project["title"]
            nodes = project_items[0]["node"]["fieldValues"]["nodes"]
            for node_item in nodes:
                # print(node_item)
                if node_item:
                    if node_item["field"]["name"] == "Deadline":
                        deadline = node_item["date"]
                    if node_item["field"]["name"] == "Started":
                        start_date = node_item["date"]
                    if node_item["field"]["name"] == "Completed":
                        complete_date = node_item["date"]
                    if node_item["field"]["name"] == "Status":
                        project_status = node_item["name"]
            # if project_items[0]["node"]["fieldValues"]["nodes"][1]["name"]:
            #     project_status = project_items[0]["node"]["fieldValues"]["nodes"][1]["name"]
            # if project_items[0]["node"]["fieldValues"]["nodes"][2]["date"]:
            #     start_date = project_items[0]["node"]["fieldValues"]["nodes"][2]["date"]
            # if project_items[0]["node"]["fieldValues"]["nodes"][4]["date"]:
            #     complete_date = project_items[0]["node"]["fieldValues"]["nodes"][4]["date"]
            # if project_items[0]["node"]["fieldValues"]["nodes"][5]["date"]:
            #     deadline = project_items[0]["node"]["fieldValues"]["nodes"][5]["date"]
        else:
            project_title = project_status = start_date = complete_date = deadline = None

        issue = Issue(issue_title, issue_url, is_closed, created_at, closed_at, project_title, project_status, start_date, complete_date, deadline)
        issue_list.append(issue)

    # Print the extracted issue items using the Issue class
    # for issue in issue_list:
    #     print(issue)
    
    print(len(issue_list))

    # Create date list of last 7 days

    # Define the date format
    date_format = "%Y-%m-%d"

    # Get the current date
    current_date = datetime.now(pytz.timezone("Asia/Dhaka"))

    # Create a list to store the dates
    date_list = []

    # Generate the list of 8 dates
    for _ in range(8):
        date_list.append(current_date.strftime(date_format))
        current_date -= timedelta(days=1)

    # Reverse the list to have the dates in descending order
    date_list.reverse()

    # Print the list of dates
    # for date in date_list:
    #     print(date)

    ## Filtering Issues
    filtered_issue_list = [issue for issue in issue_list if
                      (issue.complete_date in date_list) or
                      (issue.project_status in ["In Progress", "Open", "Reopened","Review In Progress","Need Review"])]
    
    # Sort the filtered list using the custom sorting key
    sorted_issue_list = sorted(filtered_issue_list, key=custom_sort_key)

    # Write the sorted filtered issue list to Markdown File
    directory = "output"
    if not os.path.exists(directory):
      os.makedirs(directory)

    filename = datetime.now(pytz.timezone("Asia/Dhaka")).strftime(date_format) + ".md"
    f = open(directory + "/" + filename, "w+")
    f.write(f'## Weekly Report: {datetime.now(pytz.timezone("Asia/Dhaka")).strftime("%B %d, %Y")}\n\n')
    f.write(f'**Reported By: {sys.argv[3]}**\n')
    f.write(f'\n### Status and accomplishments\n')
    f.write(f'- \n')
    f.write(f'\n### Issue Tracker\n')
    f.write("|No.|Issue Title|Status|Deadline|Comment|\n")
    f.write("|:---:|---|:---:|---|:---:|\n")
    count = 1
    for issue in sorted_issue_list:
        f.write(f'|{count}|[{issue.title}]({issue.url})|{issue.project_status}|{issue.deadline}|-|\n')
        count+=1
  
    f.write(f'\n### Issues and dependencies\n')
    f.write(f'- \n')
    f.write(f'\n### Plan for next week\n')
    f.write(f'- \n')
    f.close()

else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)


