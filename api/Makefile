# Makefile for API specification management

.PHONY: help validate serve generate-docs generate-client test test-examples

# Default target
help:
	@echo "Available commands:"
	@echo "  help           - Show this help message"
	@echo "  validate       - Validate OpenAPI specification"
	@echo "  serve          - Serve interactive documentation"
	@echo "  generate-docs  - Generate static HTML documentation"
	@echo "  generate-client- Generate TypeScript client"
	@echo "  test           - Run basic API tests (requires backend)"
	@echo "  test-examples  - Run API tests with example files"
	@echo ""
	@echo "Requirements:"
	@echo "  - Node.js and npm for tools installation"
	@echo "  - Docker (optional, for serving docs)"

# Validate OpenAPI specification
validate:
	@echo "Validating OpenAPI specification..."
	@if command -v swagger-codegen >/dev/null 2>&1; then \
		swagger-codegen validate -i openapi.yml; \
	elif command -v openapi-generator >/dev/null 2>&1; then \
		openapi-generator validate -i openapi.yml; \
	elif command -v npx >/dev/null 2>&1; then \
		npx swagger-parser validate openapi.yml; \
	else \
		echo "No validation tool found. Install swagger-codegen, openapi-generator, or swagger-parser"; \
	fi

# Serve interactive documentation using Swagger UI
serve:
	@echo "Starting Swagger UI server..."
	@if command -v docker >/dev/null 2>&1; then \
		docker run -p 8080:8080 -e SWAGGER_JSON=/api/openapi.yml -v $(PWD):/api swaggerapi/swagger-ui; \
	elif command -v npx >/dev/null 2>&1; then \
		npx swagger-ui-serve openapi.yml; \
	else \
		echo "Docker or npx required to serve documentation"; \
	fi

# Generate static HTML documentation
generate-docs:
	@echo "Generating static documentation..."
	@if command -v npx >/dev/null 2>&1; then \
		npx redoc-cli build openapi.yml --output docs/index.html; \
		echo "Documentation generated at docs/index.html"; \
	else \
		echo "npx required to generate documentation"; \
	fi

# Generate TypeScript client
generate-client:
	@echo "Generating TypeScript client..."
	@if command -v openapi-generator >/dev/null 2>&1; then \
		openapi-generator generate \
			-i openapi.yml \
			-g typescript-axios \
			-o generated/client \
			--additional-properties=npmName=review-api-client,supportsES6=true; \
		echo "Client generated in generated/client/"; \
	else \
		echo "openapi-generator required to generate client"; \
	fi

# Test API endpoints (requires running backend)
test:
	@echo "Testing API endpoints..."
	@echo "Testing POST /task/result/single"
	@curl -s -f -X POST -H "Content-Type: application/json" -d '{"user_id":"test_user"}' http://localhost:8000/api/v1/task/result/single > /dev/null && echo "✓ POST /task/result/single - OK" || echo "✗ POST /task/result/single - FAILED (may be 404 if no result)"
	@echo "Testing POST /task/result/batch"
	@curl -s -f -X POST -H "Content-Type: application/json" -d '{"user_id":"test_user"}' http://localhost:8000/api/v1/task/result/batch > /dev/null && echo "✓ POST /task/result/batch - OK" || echo "✗ POST /task/result/batch - FAILED (may be 404 if no result)"
	@echo "Testing POST /task/run/single"
	@curl -s -f -X POST -H "Content-Type: application/json" -d '{"user_id":"test_user","text":"Test text"}' http://localhost:8000/api/v1/task/run/single > /dev/null && echo "✓ POST /task/run/single - OK" || echo "✗ POST /task/run/single - FAILED"
	@echo "Testing POST /task/run/batch (requires test file)"
	@echo "test review" > test.txt && \
	curl -s -f -X POST -F "user_id=test_user" -F "file=@test.txt" http://localhost:8000/api/v1/task/run/batch > /dev/null && echo "✓ POST /task/run/batch - OK" || echo "✗ POST /task/run/batch - FAILED"; \
	rm -f test.txt

# Test with examples from curl-examples.md
test-examples:
	@echo "Testing with example data..."
	@echo "Creating test files..."
	@echo -e "text\n\"Excellent product, very satisfied!\"\n\"Quality leaves much to be desired\"\n\"Average product, nothing special\"" > test-reviews.csv
	@echo -e "Excellent product, very satisfied!\nQuality leaves much to be desired\nAverage product, nothing special" > test-reviews.txt
	@echo '[{"text":"Excellent product!"},{"text":"Poor quality"},{"text":"Average product"}]' > test-reviews.json
	
	@echo "Testing CSV upload..."
	@curl -s -X POST -F "user_id=test_user" -F "file=@test-reviews.csv" http://localhost:8000/api/v1/task/run/batch && echo "✓ CSV upload - OK" || echo "✗ CSV upload - FAILED"
	
	@echo "Testing TXT upload..."
	@curl -s -X POST -F "user_id=test_user" -F "file=@test-reviews.txt" http://localhost:8000/api/v1/task/run/batch && echo "✓ TXT upload - OK" || echo "✗ TXT upload - FAILED"
	
	@echo "Testing JSON upload..."
	@curl -s -X POST -F "user_id=test_user" -F "file=@test-reviews.json" http://localhost:8000/api/v1/task/run/batch && echo "✓ JSON upload - OK" || echo "✗ JSON upload - FAILED"
	
	@echo "Cleaning test files..."
	@rm -f test-reviews.csv test-reviews.txt test-reviews.json

# Install required tools
install-tools:
	@echo "Installing API tools..."
	@if command -v npm >/dev/null 2>&1; then \
		npm install -g @apidevtools/swagger-parser swagger-ui-serve redoc-cli; \
		echo "Tools installed successfully"; \
	else \
		echo "npm required to install tools"; \
	fi

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf generated/ docs/
	@echo "Cleaned successfully"

# Lint OpenAPI specification
lint:
	@echo "Linting OpenAPI specification..."
	@if command -v spectral >/dev/null 2>&1; then \
		spectral lint openapi.yml; \
	else \
		echo "Install spectral: npm install -g @stoplight/spectral-cli"; \
	fi

# Check for breaking changes (requires previous version)
breaking-changes:
	@echo "Checking for breaking changes..."
	@if [ -f "openapi.prev.yml" ] && command -v oasdiff >/dev/null 2>&1; then \
		oasdiff breaking openapi.prev.yml openapi.yml; \
	else \
		echo "oasdiff tool or previous version file required"; \
	fi

# Bundle specification into single file (resolve $ref)
bundle:
	@echo "Bundling OpenAPI specification..."
	@if command -v npx >/dev/null 2>&1; then \
		npx swagger-jsdoc -d openapi.yml -o openapi.bundled.yml; \
	else \
		echo "npx required for bundling"; \
	fi
