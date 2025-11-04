from mcp.server.fastmcp import FastMCP
import os
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

mcp = FastMCP("mcp server")

client = Client()
client.set_config({
    "api_key": os.getenv("MAILCHIMP_API_KEY"),
    "server": "us21"  # your datacenter prefix
})

@mcp.tool()
def add_subscriber(name:str, email:str ):
    try:
        response = client.lists.add_list_member(
            os.getenv("MAILCHIMP_LIST_ID"),
            {"name": name,"email_address": email, "status": "subscribed"}
        )
        return f"Successfully enetered the user , {response}"
    except ApiClientError as error:
        return f"Error: the user was not added , {error}"
  
@mcp.tool()
def tag_subscriber(email: str, tag: str):
    pass

@mcp.tool()
def send_campaign(subject: str, content: str, recipients: list[str]):
    """
    Create a Mailchimp campaign and send it to a list of recipients.
    """
    try:
        # 1. You must first have a list/audience in Mailchimp
        list_id = os.getenv("MAILCHIMP_LIST_ID")

        # 2. Create a campaign
        campaign = client.campaigns.create({
            "type": "regular",
            "recipients": {
                "list_id": list_id
            },
            "settings": {
                "subject_line": subject,
                "from_name": "Your Company",
                "reply_to": "noreply@yourcompany.com"
            }
        })

        campaign_id = campaign["id"]

        # 3. Set the content for the campaign
        client.campaigns.set_content(
            campaign_id,
            {
                "html": content
            }
        )

        # 4. Send the campaign
        client.campaigns.send(campaign_id)
        return f" Successfully created and sent campaign {campaign_id}"
    except Exception as e:
        return f"Error: campaign not created. {str(e)}"

@mcp.tool()
def get_reports(campaign_id:str): # getting campaign from single campaign ID
    """
    Retrieve open/click/bounce statistics for a Mailchimp campaign.
    """
    try:
        report = client.reports.get_campaign_report(campaign_id)
       
        return {
            "emails_sent": report["emails_sent"],
            "open_rate": report["opens"]["open_rate"],
            "click_rate": report["clicks"]["click_rate"],
            "bounces": report["bounces"]["hard_bounces"] + report["bounces"]["soft_bounces"],
            "unsubscribes": report["unsubscribed"]
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_all_reports(count: int = 10, offset: int = 0): # this is the list of campaigns. 
    """
    List analytics for multiple Mailchimp campaigns.
    count: how many campaigns to fetch
    offset: pagination offset
    """
    try:
        reports = client.reports.get_all_campaign_reports(
            counts = count,
            offset = offset
        )
        # we can shape the JSON to the dashboard’s needs
        campaign_summary = []
        for report in reports["reports"]:
            campaign_summary.append({"campaign_id": report["id"],
                "campaign_name": report["campaign_title"],
                "emails_sent": report["emails_sent"],
                "open_rate": report["opens"]["open_rate"],
                "click_rate": report["clicks"]["click_rate"],
                "send_time": report["send_time"]}
            )
        return campaign_summary
            
    except Exception as e:
        return {"error": str(e)}

