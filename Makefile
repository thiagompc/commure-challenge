.PHONY: setup activate install run test clean

# Create a virtual environment
setup:
	python3 -m venv venv

# Activate the virtual environment
activate:
	@echo "Run 'source venv/bin/activate' to activate the virtual environment."

# Install project dependencies
install: setup
	venv/bin/pip install -r requirements.txt

# Run the project
run:
	venv/bin/python3 main.py

# Run tests
test:
	venv/bin/python3 -m unittest

# Clean up the virtual environment
clean:
	rm -rf venv
