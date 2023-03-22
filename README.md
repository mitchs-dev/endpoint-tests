# Table of contents

- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Configuration](#configuration)
  - [maxWorkers](#maxworkers)
- [Tests](#tests)
  - [loadTesting](#loadtesting)
    - [apiLoadTesting](#apiloadtesting)
      - [simpleLoadTest](#simpleloadtest)
      - [creationLoadTest](#creationloadtest)
    - [uiLoadTesting](#uiloadtesting)
- [exampleConfigFile](#exampleconfigfile)
- [disclaimer](#disclaimer)

# Introduction

Planned to be an 'all-in-one' simple testing platform for various infrastructure using only one `YAML` file.

# Requirements

1. Python [3.10](https://www.python.org/downloads/release/python-3100/)+
2. Run: `pip3 install -r requirements.txt` in root directory.
3. Create `config.yaml` in root directory with the configuration options below. (See [exampleConfigFile](#exampleconfigfile) for full configuration values)

# Configuration

Each test contains it's own set of configurable options, but there are some global configuration items which are mentioned below.

```yaml
config:
  baseUrl: "https://example.domain.com" # The base URL for the service which you are testing
  debugMode: false # Enable debug mode (default: false)
  maxWorkers: 10 # Set maximum worker threads to use (default: 10)
  requestTimeout: 30 # Set request timeout value [in seconds] (default: 30)
credentials: # Credentials to be used for various endpoints stored in a disctionary structure
  - name: "example-credential" # Name to ID your credential
    type: "header" # Type of credential - Currently only 'header' is supported
    key: "Authorization" # Key to use for the 'header' credential (commonly: Authorization)
    value: "my.API.token.Value" # Value to use for the 'header' credential (I.e API token)
```

## maxWorkers

Max workers lets you define the maximum worker threads to allocate during execution. You can fine tune this to your environment. However, it's a good idea to keep in mind that you should increase this with caution with higher thread counts as this could potentially be _very_ performance heavy. Each test will have an option to define request counts so if you require several requests to be made, you can still make these requests with a lower worker thread count. Alternatively, you can always horizontally scale your testing to a different client node.

# Tests

## loadTesting

The load testing category provides a performance anaylsis of an API endpoint by sending x requests in parallel using the config-defined worker threads.

Here are the configurable options for the load testing category

```yaml
categories: # All categories which can be configured for the tool
  loadTest: # The configuration values for the load testing category
    enable: true # Enable the load test category (default: true)
```

### apiLoadTesting

The API load testing tests are specifically designed to probe API endpoints. These tests in their current state are simple, but could be expanded in the future. 

Here are the configurable options for the API load testing category

```yaml
categories: # All categories which can be configured for the tool
  loadTest: # The configuration values for the load testing category
    tests: # Tests available within the load testing category
      api: # The API load testing tests
        enable: true # Enable API load testing tests (default: true)
        path: "/api/" # The path which your API is available at
```

Below are the details for the suite of tests available for API testing.

1. [simpleLoadTest](#simpleloadtest)
2. [creationLoadTest](#creationloadtest)



#### simpleLoadTest

Designed to run `requestCount` number of endpoint connection checks.

```yaml
categories: # All categories which can be configured for the tool
  loadTest: # The configuration values for the load testing category
    tests: # Tests available within the load testing category
      api: # The API load testing tests
        suite: # The suite of tests available for API load testing
          simpleLoadTest: # Configuation values for simple load test
            enable: true # Enable simple load test (default: true)
            endpoint: "ping" # Endpoint to test
            requestCount: 100 # Requests to send (default: 100)
            failureThreshhold: 1 # Amount of acceptable failures (Default: 1)
            credentials: # Credentials to authenticate with for the endpoint
              required: true # Require credentials (default: true)
              name: "example-credential" # Credentials to use in 'credentials' dictionary
```

#### creationLoadTest

Designed to create and (optionally) delete `requestCount` resources at a defined endpoint.

```yaml
categories: # All categories which can be configured for the tool
  loadTest: # The configuration values for the load testing category
    tests: # Tests available within the load testing category
      api: # The API load testing tests
        suite: # The suite of tests available for API load testing
          creationLoadTest: # Configuation values for creation load test
            enable: false # Enable configuration load test (default: true)
            sets: # Dictionary of endpoints to create/delete resources
              - name: "account-creation" # Name to ID endpoint
                enable: true # Enable the endpoint (default: true)
                create: # Configuration options for creating resources
                  endpoint: "admin/accounts" # Endpoint to hit
                delete: # Configuration options for deleting resources
                  enable: true # Enable resource deletion (default: true)
                  endpoint: "admin/accounts" # Endpoint to hit
                requestCount: 100 # Amount of times to create/delete resources (default: 100)
                failureThreshhold: 1 # Amount of acceptable failures (Default: 1)
            credentials: # Credentials to authenticate with for the endpoint
              required: true # Require credentials (default: true)
              name: "example-credential" # Credentials to use in 'credentials' dictionary
```

### uiLoadTesting

UI load testing is currently unavailable. If you try to run this module, you'll see output similar to:

```
----- LOAD TESTING -----
[...]
--> loadTesting.ui [2/2]
Run UI Test
TBD
```

Here are the configurable options for the API load testing category

```yaml
categories: # All categories which can be configured for the tool
  loadTest: # The configuration values for the load testing category
    tests: # Tests available within the load testing category
      ui: # The UI load testing tests
        enable: false # Enable UI load testing tests (default: false)
```

# exampleConfigFile

**IMPORTANT**: It's suggested to simply copy and paste this configuration and update values as needed as all values should be considered _required_.

```yaml
config: # Global configuration values for the tool
  baseUrl: "https://example.domain.com" # The base URL for the service which you are testing
  debugMode: false # Enable debug mode (default: false)
  maxWorkers: 10 # Set maximum worker threads to use (Default: 10)
  requestTimeout: 30 # Set request timeout value [in seconds] (default: 30)
credentials: # Credentials to be used for various endpoints stored in a disctionary structure
  - name: "example-credential" # Name to ID your credential
    type: "header" # Type of credential - Currently only 'header' is supported
    key: "Authorization" # Key to use for the 'header' credential (commonly: Authorization)
    value: "my.API.token.Value" # Value to use for the 'header' credential (I.e API token)
categories: # All categories which can be configured for the tool
  loadTest: # The configuration values for the load testing category
    enable: true # Enable the load test category (default: true)
    tests: # Tests that reside within a category
      api: # The API load testing tests
        enable: true # Enable API load testing tests (default: true)
        path: "/api/" # The path which your API is available at
        suite: # The suite of tests available for API load testing
          creationLoadTest: # Configuation values for creation load test
            enable: false # Enable configuration load test (default: true)
            sets: # Dictionary of endpoints to create/delete resources
              - name: "account-creation" # Name to ID endpoint
                enable: true # Enable the endpoint (default: true)
                create: # Configuration options for creating resources
                  endpoint: "admin/accounts" # Endpoint to hit
                delete: # Configuration options for deleting resources
                  enable: true # Enable resource deletion (default: true)
                  endpoint: "admin/accounts" # Endpoint to hit
                requestCount: 100 # Amount of times to create/delete resources (default: 100)
                failureThreshhold: 1 # Amount of acceptable failures (Default: 1)
            credentials: # Credentials to authenticate with for the endpoint
              required: true # Require credentials (default: true)
              name: "example-credential" # Credentials to use in 'credentials' dictionary
          creationLoadTest: # Configuation values for creation load test
            enable: false # Enable configuration load test (default: true)
            sets: # Dictionary of endpoints to create/delete resources
              - name: "account-creation" # Name to ID endpoint
                enable: true # Enable the endpoint (default: true)
                create: # Configuration options for creating resources
                  endpoint: "admin/accounts" # Endpoint to hit
                delete: # Configuration options for deleting resources
                  enable: true # Enable resource deletion (default: true)
                  endpoint: "admin/accounts" # Endpoint to hit
                requestCount: 100 # Amount of times to create/delete resources (default: 100)
                failureThreshhold: 1 # Amount of acceptable failures (Default: 1)
            credentials: # Credentials to authenticate with for the endpoint
              required: true # Require credentials (default: true)
              name: "example-credential" # Credentials to use in 'credentials' dictionary
      ui: # The UI load testing tests
        enable: false # Enable UI load testing tests (default: false)
   
```
# disclaimer

This tool works as is. But some parts were customized to be used for my own purposes and may be restrictive for various endpoint testing. However, feel free to push a PR or fork it for your own needs. Make sure to read [LICENSE](LICENSE) for additional details on how this project can be used.
