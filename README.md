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

## Getting Started

### Prerequisites
- Python 3.12 or higher
- [Rye](https://rye-up.com/guide/installation/) for dependency management

### Installation
1. Clone the repository
2. Install dependencies using Rye
   ```
   rye sync
   ```
3. Set up environment variables:
   Create a `.env` file in the project root by copying `.env.default`:
   ```
   cp .env.default .env
   ```
   You can then modify the variables in `.env` as needed.


### Running the Service
Start the FastAPI server using the script defined in pyproject.toml:
   ```
   rye run start
   ```

The API will be available at `http://localhost:8000`.

#### API Documentation

Once the server is running, you can access the interactive API documentation:

- Swagger UI: Available at `/docs`
- ReDoc: Available at `/redoc`

These interfaces provide detailed information about all available endpoints, request/response schemas, and allow you to test the API directly from your browser.

### Usage

To anonymize an xAPI trace, send a POST request to the `/anonymize` endpoint.

**Example Request**

```http
curl -X POST http://localhost:8000/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "trace": {
      "data": {
        "actor": {
          "name": "John Doe",
          "account": {
            "name": "johndoe",
            "homePage": "https://example.com"
          }
        },
        "object": {
          "id": "http://example.com/activities/course-001",
          "definition": {
            "extensions": {
              "http://id.tincanapi.com/extension/browser-info": "Chrome/91.0",
              "http://id.tincanapi.com/extension/ip-address": "192.168.1.1",
              "http://id.tincanapi.com/extension/geojson": "45.123°N 2.345°E"
            }
          }
        },
        "verb": {
          "id": "http://example.com/verbs/completed"
        }
      }
    }
  }'
```

**Example Response**
```json
{
  "trace": {
    "data": {
      "actor": {
        "name": "Anonymous",
        "account": {
          "name": "Anonymous",
          "homePage": "https://anonymous.org"
        }
      },
      "object": {
        "id": "http://example.com/activities/course-001",
        "definition": {}
      },
      "verb": {
        "id": "http://example.com/verbs/completed"
      }
    }
  }
}
```

### Development

#### Code Formatting and Linting

The project uses Ruff for linting and formatting. Ruff is configured in `pyproject.toml` with strict settings:
- All rules enabled by default
- Python 3.12 target version
- 88 character line length
- Custom rule configurations for specific project needs

### Environment Variables

The following table details the environment variables used in the project:

| Variable | Description | Required | Default Value | Possible Values |
|----------|-------------|----------|---------------|-----------------|
| ENVIRONMENT | Affects error handling and logging throughout the application | No | development | development, production |
| LOG_LEVEL | Minimum logging level for the application | No | info | debug, info, warning, error, critical |

Refer to `.env.default` for a complete list of configurable environment variables and their default values.
