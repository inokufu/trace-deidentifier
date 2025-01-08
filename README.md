# Trace Deidentifier

<!-- TOC -->
* [Trace Deidentifier](#trace-deidentifier)
  * [Overview](#overview)
  * [Objectives](#objectives)
  * [How It Works](#how-it-works)
    * [Anonymization Principles](#anonymization-principles)
    * [Data Processing](#data-processing)
      * [Anonymized Agents](#anonymized-agents)
      * [Agent Locations Processed](#agent-locations-processed)
      * [Removed Extensions](#removed-extensions)
  * [Setup and installation](#setup-and-installation)
    * [With Docker](#with-docker)
      * [Prerequisites](#prerequisites)
      * [Development Environment](#development-environment)
      * [Quick Start (Without volumes or Traefik)](#quick-start-without-volumes-or-traefik)
      * [Production Environment](#production-environment)
    * [With Rye](#with-rye)
      * [Prerequisites](#prerequisites-1)
      * [Installation](#installation)
      * [Running the Application](#running-the-application)
  * [Usage](#usage)
  * [Development](#development)
    * [API Documentation](#api-documentation)
    * [Code Formatting and Linting](#code-formatting-and-linting)
    * [Environment Variables](#environment-variables)
<!-- TOC -->


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
- Replacement of sensitive data with anonymized values
- Removal of non-required fields containing personal information
- Recursive processing of nested structures (SubStatements)

### Data Processing

#### Anonymized Agents
The following fields are anonymized for all agents (Actor, Group Members, Object Agents, Context Agents, Authority):
- name (learner's name) → "Anonymous"
- mbox (email) →  "mailto:anonymous@anonymous.org"
- mbox_sha1sum (email hash) → SHA1 hash of "mailto:anonymous@anonymous.org"
- openid → "https://anonymous.org/anonymous"
- account.name → "Anonymous"
- account.homePage → "https://anonymous.org"

#### Agent Locations Processed
- actor (primary agent/group)
- actor.member (for groups)
- object (when objectType is "Agent" or "Group")
- authority (including OAuth groups)
- context.instructor
- context.team
- SubStatements (recursive processing of all the above fields)

#### Removed Extensions
- Browser extensions (http://id.tincanapi.com/extension/browser-info)
- IP address (http://id.tincanapi.com/extension/ip-address)
- Geolocation data (http://id.tincanapi.com/extension/geojson)
- Invited/observer actor information (http://id.tincanapi.com/extension/referrer, http://id.tincanapi.com/extension/invitee and http://id.tincanapi.com/extension/observer)
- Social media references (http://id.tincanapi.com/extension/tweet)

## Setup and installation

You can run the application either directly with **Rye** or using **Docker**.

1. Clone the repository
2. Set up environment variables:
   Create a `.env` file in the project root by copying `.env.default`:
   ```
   cp .env.default .env
   ```
   You can then modify the variables in `.env` as needed.

### With Docker

The application is containerized using Docker, with a robust and flexible deployment strategy that leverages:
- Docker for containerization with a multi-environment support (dev and prod) using Docker Compose profiles
- Traefik as a reverse proxy and load balancer, with built-in SSL/TLS support via Let's Encrypt, and a dashboard in dev environment.
- Gunicorn as the production-grade WSGI HTTP server, with configurable worker processes and threads, and dynamic scaling based on system resources.

#### Prerequisites

- Docker and Docker Compose installed on your machine.

#### Development Environment

Build and run the development environment:
```
docker-compose --profile dev up --build
```

The API will be available at : `http://deidentifier.localhost`

Traefik Dashboard will be available at : `http://traefik.deidentifier.localhost`

#### Quick Start (Without volumes or Traefik)
For a quick test without full stack:
```
docker build --target dev-standalone -t deidentifier:dev-standalone .
docker run --env-file .env -p 8001:8001 deidentifier:dev-standalone
```
Note: This version won't reflect source code changes in real-time.

#### Production Environment

Configure production-specific settings, then build and run the production environment:
```
docker-compose --profile prod up --build
```

### With Rye

#### Prerequisites
- Python 3.12 or higher
- [Rye](https://rye.astral.sh/) for dependency management

#### Installation
1. Install Rye, see https://rye.astral.sh/guide/installation/
2. Install dependencies using Rye
   ```
   rye sync
   ```
3. Start the FastAPI server using the script defined in pyproject.toml
   ```
   rye run start
   ```

#### Running the Application

The API will be available at `http://localhost:8001`.

## Usage

To anonymize an xAPI trace, send a POST request to the `/anonymize` endpoint.

**Example Request**

```http
curl -X POST http://localhost:8001/anonymize \
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

## Development

### API Documentation

Once the server is running, you can access the interactive API documentation:

- Swagger UI: Available at `/docs`
- ReDoc: Available at `/redoc`

These interfaces provide detailed information about all available endpoints, request/response schemas, and allow you to test the API directly from your browser.

### Code Formatting and Linting

The project uses Ruff for linting and formatting. Ruff is configured in `pyproject.toml` with strict settings:
- All rules enabled by default
- Python 3.12 target version
- 88 character line length
- Custom rule configurations for specific project needs

### Environment Variables

The following table details the environment variables used in the project:

| Variable | Description | Required | Default Value | Possible Values |
|----------|-------------|----------|--------------|-----------------|
| **Environment Configuration** | | | | |
| `ENVIRONMENT` | Affects error handling and logging throughout the application | No | `development` | `development`, `production` |
| `LOG_LEVEL` | Minimum logging level | No | `info` | `debug`, `info`, `warning`, `error`, `critical` |
| **Internal Application Configuration** | | | | |
| `APP_INTERNAL_HOST` | Host for internal application binding | No | `0.0.0.0` | Valid host/IP |
| `APP_INTERNAL_PORT` | Port for internal application binding | No | `8001` | Any valid port |
| **External Routing Configuration** | | | | |
| `APP_EXTERNAL_HOST` | External hostname for the application | Yes | `deidentifier.localhost` | Valid hostname |
| `APP_EXTERNAL_PORT` | External port for routing (dev env only) | No | `80` | Any valid port |
| **Traefik Configuration** | | | | |
| `TRAEFIK_RELEASE` | Traefik image version | No | `v3.2.3` | Valid Traefik version |
| `LETS_ENCRYPT_EMAIL` | Email for Let's Encrypt certificate | Yes | `test@example.com` | Valid email |
| **Performance Configuration** | | | | |
| `WORKERS_COUNT` | Number of worker processes | No | `4` | Positive integer |
| `THREADS_PER_WORKER` | Number of threads per worker | No | `2` | Positive integer |

Refer to `.env.default` for a complete list of configurable environment variables and their default values.
