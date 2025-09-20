
# N8N Integration Documentation

## Overview
This document describes the N8N integration for the Purdue CS Curriculum scraper.

## Workflow Structure

### 1. Schedule Trigger
- **Type**: Cron trigger
- **Schedule**: Weekly (Sundays at midnight)
- **Purpose**: Automatically start the data pipeline

### 2. Execute Scraper
- **Type**: Command execution
- **Command**: `node advanced_scraper/purdue_scraper.js scrape all -o json`
- **Purpose**: Extract curriculum data from Purdue CS website

### 3. Process Data
- **Type**: Command execution
- **Command**: `node advanced_scraper/data_processor.js process data/advanced_curriculum_data.json`
- **Purpose**: Transform raw data into structured format

### 4. Validate Data
- **Type**: Function node
- **Purpose**: Ensure data quality and completeness

### 5. Update Knowledge Graph
- **Type**: Function node
- **Purpose**: Update the knowledge graph with new data

### 6. Notify Completion
- **Type**: HTTP request
- **Purpose**: Send completion notification

## Configuration

### Environment Variables
- `N8N_WEBHOOK_URL`: Webhook URL for triggering workflows
- `N8N_WORKFLOW_ID`: ID of the curriculum pipeline workflow

### Webhook Endpoints
- `/webhook/purdue-cs`: Main trigger endpoint
- `/webhook/purdue-cs/sync`: Data synchronization endpoint

## Monitoring
- Workflow status monitoring
- Success/failure notifications
- Performance metrics tracking

## Usage

### Manual Trigger
```javascript
const integration = new N8NIntegration();
await integration.triggerWorkflow();
```

### Data Sync
```javascript
await integration.syncData('path/to/data.json');
```

### Pipeline Creation
```javascript
await integration.createDataPipeline();
```

## Error Handling
- Automatic retry on failures
- Error notifications
- Data validation checks
- Rollback capabilities

## Security
- API authentication
- Rate limiting
- Data encryption
- Access control
