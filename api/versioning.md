# API Versioning Strategy

## Current Version
- **Version**: 1.0.0
- **Base Path**: `/api/v1`
- **Status**: Active Development

## Versioning Approach

### Semantic Versioning
API следует семантическому версионированию (SemVer):
- **Major (1.x.x)** - Breaking changes
- **Minor (x.1.x)** - New features, backward compatible  
- **Patch (x.x.1)** - Bug fixes, backward compatible

### URL Versioning
API использует версионирование через URL path:
```
/api/v1/task/result/single
/api/v1/task/result/batch
```

## Backward Compatibility

### Non-Breaking Changes (Patch/Minor)
- Adding new endpoints
- Adding optional fields in response
- Adding optional request parameters
- Documentation improvements
- Bug fixes

### Breaking Changes (Major)
- Removing endpoints
- Changing data types of existing fields
- Changing field requirements
- Changing response structure
- Changing HTTP methods

## Migration Strategy

### Deprecation Process
1. **Announce** - Deprecation notification in documentation
2. **Mark** - Adding deprecated flags in OpenAPI
3. **Support** - Supporting old version for at least 6 months
4. **Remove** - Removal in next major version

### Version Transition
```yaml
# Example deprecation in OpenAPI
paths:
  /reviews/old-endpoint:
    get:
      deprecated: true
      description: "⚠️ DEPRECATED: Use /reviews/ instead. Will be removed in v2.0.0"
```

## Version History

### v1.0.0 (Current)
**Task-based API Architecture**

#### New Endpoints
- `POST /api/v1/task/result/single` - Get last single task result
- `POST /api/v1/task/result/batch` - Get last batch task result  
- `POST /api/v1/task/run/single` - Send task for single text analysis
- `POST /api/v1/task/run/batch` - Send task for batch file analysis

#### Key Features
- User-based task management via `user_id` parameter
- Unified task response format with status tracking
- Support for multiple file formats (CSV, TXT, JSON)
- File size limit: 10MB maximum
- Text length limit: 512 characters for single analysis
- Comprehensive error handling with specific error codes
- Unix timestamp tracking for task start/end times

#### API Changes
- All endpoints now use POST method for consistency
- User identification required for all operations
- Task-based response structure with status, start/end times
- Structured error responses with codes 01, 02, 03
- Enhanced batch result format with percentage calculations


## Monitoring

### API Metrics
- Version usage statistics
- Deprecated endpoint access patterns
- Error rates by version
- Performance metrics by version

### Health Checks
```
GET /api/v1/health
GET /api/version-info
```

## Best Practices

1. **Never break existing functionality** without major version bump
2. **Always provide migration paths** for breaking changes
3. **Document all changes** in changelog
4. **Test backward compatibility** thoroughly
5. **Monitor usage patterns** before deprecating features
6. **Communicate changes** to API consumers early

## Tools and Automation

### Version Management
- OpenAPI diff tools for change detection
- Automated compatibility testing
- Version-specific documentation generation

### Commands
```bash
# Check for breaking changes
make breaking-changes

# Validate specification
make validate

# Generate client for specific version
openapi-generator generate -i openapi.yml -g typescript-axios --additional-properties=npmVersion=1.0.0
```
