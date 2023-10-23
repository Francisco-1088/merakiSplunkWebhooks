import meraki

import config

dashboard = meraki.DashboardAPI(api_key=config.api_key)

organizations = dashboard.organizations.getOrganizations()

for org in organizations:
    if org['name']==config.organization_name:
        org_id = org['id']

if org_id:
    if config.tag!="":
        networks = dashboard.organizations.getOrganizationNetworks(org_id, tags=config.tag)
    else:
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

for net in networks:
    body = '''
    {
      "time":{{sentAt | date:"%s"}},
      "host": "api.meraki.com",
      "source": "{{networkName}}",
      "sourceType":"main",
      "event" : {
        "sentAt": "{{sentAt}}",
        "organizationId": "{{organizationId}}",
        "organizationName": "{{organizationName}}",
        "organizationUrl": "{{organizationUrl}}",
        "networkId": "{{networkId}}",
        "networkName": "{{networkName}}",
        "networkUrl": "{{networkUrl}}",
        "networkTags": {{ networkTags | jsonify }},
        "deviceSerial": "{{deviceSerial}}",
        "deviceMac": "{{deviceMac}}",
        "deviceName": "{{deviceName}}",
        "deviceUrl": "{{deviceUrl}}",
        "deviceTags": {{ deviceTags | jsonify }},
        "deviceModel": "{{deviceModel}}",
        "alertId": "{{alertId}}",
        "alertType": "{{alertType}}",
        "alertTypeId": "{{alertTypeId}}",
        "alertLevel": "{{alertLevel}}",
        "occurredAt": "{{occurredAt}}",
        "alertData": {{ alertData | jsonify }}
      }
    }
    '''
    headers = [
        {
            "name": "Authorization",
            "template": "Splunk {{sharedSecret}}"
        }
    ]

    result = dashboard.networks.createNetworkWebhooksPayloadTemplate(
        networkId=net['id'],
        name=f"Splunk_{net['id']}",
        body=body,
        headers=headers,
    )

    splunk_webhook = {
        "sharedSecret": config.splunk_webhook_auth,
        "payloadTemplate": {
            "payloadTemplateId": result['payloadTemplateId'],
            "name": f"Splunk_{net['id']}",
        }
    }

    
    dashboard.networks.createNetworkWebhooksHttpServer(
        networkId=net['id'],
        name=config.splunk_webhook_name,
        url=config.splunk_webhook_url,
        **splunk_webhook
    )
