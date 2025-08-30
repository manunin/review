# Mock System

A comprehensive mock system for task-based sentiment analysis operations, enabling frontend development and testing without backend dependencies.

## Overview

This mock system simulates the backend API for task-based operations, providing realistic data generation and error scenarios for development and testing purposes.

## Files Structure

- **`config.ts`** - Mock configuration and error scenarios
- **`data-generators.ts`** - Data generation utilities for tasks, results, and analytics
- **`api-mock.service.ts`** - Mock API service implementation
- **`index.ts`** - Main export file for all mock functionality

## Key Features

- **Realistic Data Generation**: Generates tasks, sentiment analysis results, and analytics
- **Error Simulation**: Configurable error scenarios for testing error handling
- **Task-based Operations**: Supports single text analysis and batch file processing
- **Development Mode**: Seamless integration with development workflow
- **TypeScript Support**: Full type safety with comprehensive interfaces

## Usage

### Enabling Mock System

The mock system is automatically enabled in development mode and can be configured via environment variables:

```bash
# .env.development
VITE_MOCK_ENABLED=true
VITE_DEBUG_MODE=true
VITE_API_BASE_URL=/api/v1
```

### For Developers

1. **Automatic Mode** (Recommended):
   - Mock system activates automatically when `NODE_ENV=development`
   - No additional configuration needed

2. **Manual Control**:
   ```typescript
   // In your component or service
   import { useTaskStore } from '@/store'
   
   const taskStore = useTaskStore()
   
   // Check if mock mode is active
   console.log('Mock mode:', taskStore.isDevelopmentMode)
   
   // Toggle mock mode programmatically (development only)
   taskStore.toggleMockMode()
   ```

3. **Environment Setup**:
   ```bash
   # Development with mocks
   npm run dev
   
   # Development with real API
   VITE_MOCK_ENABLED=false npm run dev
   ```

4. **Console Debugging**:
    ```javascript
    // В browser console
    window.__mockUtils.enableMockMode()
    window.__mockUtils.getDevInfo()
    ```

### Usage in Components

```vue
<script setup lang="ts">
import { useTaskStore } from '@/store'

const taskStore = useTaskStore()

// Single text analysis
const analyzeText = async (text: string) => {
  const result = await taskStore.analyzeSingleText(text)
  console.log('Analysis result:', result)
}

// Batch file processing
const processBatch = async (file: File) => {
  const result = await taskStore.analyzeBatchFile(file)
  console.log('Batch result:', result)
}
</script>
```

## API Endpoints Simulated

- `POST /api/v1/tasks/single` - Single text analysis
- `POST /api/v1/tasks/batch` - Batch file processing
- `GET /api/v1/tasks/result/single` - Get single task result
- `GET /api/v1/tasks/result/batch` - Get batch task result

## Configuration

Mock behavior can be customized in `config.ts`:

- Enable/disable specific error scenarios
- Adjust response delays
- Configure data generation parameters
- Set success/failure rates

## Integration

The mock system integrates seamlessly with:
- **TaskStore** (Pinia store)
- **TaskService** (Service layer)
- **ApiService** (HTTP client wrapper)

No code changes required when switching between mock and real API endpoints.
