#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
BUILD_TYPE="all"
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
DOCKER_TAG="vmware-vra-cli:${VERSION}"

# Help function
show_help() {
    cat << EOF
VMware vRA CLI Server Build Script

Usage: ./scripts/build.sh [OPTIONS]

OPTIONS:
    -t, --type TYPE     Build type: wheel, docker, compose, all (default: all)
    -v, --version VER   Version tag for Docker (default: from pyproject.toml)
    -h, --help          Show this help message

BUILD TYPES:
    wheel              Build Python wheel package
    docker             Build Docker image
    compose            Build and start with docker-compose
    all                Build wheel and Docker image (default)

EXAMPLES:
    ./scripts/build.sh                     # Build everything
    ./scripts/build.sh -t wheel            # Build only Python wheel
    ./scripts/build.sh -t docker           # Build only Docker image
    ./scripts/build.sh -t docker -v 1.0.0  # Build Docker image with custom tag
    ./scripts/build.sh -t compose          # Build and start with docker-compose

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            DOCKER_TAG="vmware-vra-cli:${VERSION}"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate build type
case $BUILD_TYPE in
    wheel|docker|compose|all)
        ;;
    *)
        print_error "Invalid build type: $BUILD_TYPE"
        print_error "Valid types: wheel, docker, compose, all"
        exit 1
        ;;
esac

print_status "VMware vRA CLI Server Build Script"
print_status "Version: $VERSION"
print_status "Build Type: $BUILD_TYPE"
echo

# Function to build Python wheel
build_wheel() {
    print_status "Building Python wheel..."
    
    # Install dependencies
    if command -v uv &> /dev/null; then
        uv sync --extra dev
    else
        print_error "uv is required but not installed. Please install uv first."
        exit 1
    fi
    
    # Run tests
    print_status "Running tests..."
    uv run pytest tests/test_server.py -v
    
    # Build package
    print_status "Building package..."
    uv build
    
    # Show build artifacts
    print_success "Python wheel built successfully!"
    echo "Build artifacts:"
    ls -la dist/*.whl dist/*.tar.gz 2>/dev/null || true
}

# Function to build Docker image
build_docker() {
    print_status "Building Docker image: $DOCKER_TAG"
    
    # Build Docker image
    docker build -t "$DOCKER_TAG" .
    
    # Tag as latest if this is the default version
    if [[ "$DOCKER_TAG" != *":"* ]] || [[ "$VERSION" == "$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')" ]]; then
        docker tag "$DOCKER_TAG" "vmware-vra-cli:latest"
        print_status "Tagged as vmware-vra-cli:latest"
    fi
    
    print_success "Docker image built successfully!"
    echo "Docker images:"
    docker images | grep vmware-vra-cli || true
}

# Function to build and start with docker-compose
build_compose() {
    print_status "Building with docker-compose..."
    
    # Build and start services
    docker-compose build
    docker-compose up -d
    
    # Wait for service to be healthy
    print_status "Waiting for service to be healthy..."
    timeout 60 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 2; done'
    
    print_success "Docker Compose deployment successful!"
    echo "Service status:"
    docker-compose ps
    echo
    print_status "Server is running at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    echo
    print_status "To stop: docker-compose down"
    print_status "To view logs: docker-compose logs -f"
}

# Execute based on build type
case $BUILD_TYPE in
    wheel)
        build_wheel
        ;;
    docker)
        build_docker
        ;;
    compose)
        build_compose
        ;;
    all)
        build_wheel
        echo
        build_docker
        ;;
esac

print_success "Build completed successfully!"

# Show next steps
echo
print_status "Next Steps:"
case $BUILD_TYPE in
    wheel)
        echo "  • Install: pip install dist/vmware_vra_cli-${VERSION}-py3-none-any.whl"
        echo "  • Run server: vra-server"
        ;;
    docker)
        echo "  • Run container: docker run -p 8000:8000 $DOCKER_TAG"
        echo "  • Access API docs: http://localhost:8000/docs"
        ;;
    compose)
        echo "  • Server is already running at: http://localhost:8000"
        echo "  • Stop: docker-compose down"
        ;;
    all)
        echo "  • Install wheel: pip install dist/vmware_vra_cli-${VERSION}-py3-none-any.whl"
        echo "  • Run container: docker run -p 8000:8000 $DOCKER_TAG"
        echo "  • Or use compose: docker-compose up -d"
        ;;
esac
