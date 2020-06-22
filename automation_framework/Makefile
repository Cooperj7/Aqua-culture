init: install-env db

start:
	echo "!!!!!!!!!!!!This should only be used for testing!!!!!!!!!!!!"
	python3 -m "framework_controller"

install-env:
	./install_environment.sh

db:
	python3 -c "from framework.database.database import create_database; create_database()"

system-test:
	python3 -m "tests.system_check"

sensor-test:
	python3 -m "tests.test_sensor_output"

clean:
	rm -r venv-framework
	find . -type f -name '*.log' -delete

reset: clean init
