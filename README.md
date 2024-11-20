# Trace Deidentifier
## Overview
xAPI trace anonymization module.
This component enables the anonymization of personal data in learning traces to facilitate secure data sharing between trusted organizations.


## Objectives
- Anonymize xAPI traces while preserving their analytical value
- Enable data sharing between organizations without compromising user privacy
- Facilitate data usage for statistics and AI training
- Ensure compliance with privacy standards and best practices

## How It Works
### Anonymization Principles
- Replacement of sensitive data with the value "anonymous"
- Removal of non-required fields containing personal information

### Data Processing
#### Removed Data
- actor.name (learner's name)
- actor.mbox (email)
- actor.mbox_sha1sum (email hash)
- actor.account.name
- actor.account.homePage
- Browser extensions (http://id.tincanapi.com/extension/browser-info)
- IP address (http://id.tincanapi.com/extension/ip-address)
- Geolocation data (http://id.tincanapi.com/extension/geojson)
- Invited/observer actor information (http://id.tincanapi.com/extension/referrer, http://id.tincanapi.com/extension/invitee and http://id.tincanapi.com/extension/observer)
- Social media references (http://id.tincanapi.com/extension/tweet)
